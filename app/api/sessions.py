from flask.ext.restplus import Namespace, reqparse
from sqlalchemy.orm.collections import InstrumentedList

from app.helpers.data import record_activity, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.notification_email_triggers import trigger_new_session_notifications, \
    trigger_session_schedule_change_notifications
from app.helpers.notification_email_triggers import trigger_session_state_change_notifications
from app.models.microlocation import Microlocation as MicrolocationModel
from app.models.session import Session as SessionModel
from app.models.session_type import SessionType as SessionTypeModel
from app.models.speaker import Speaker as SpeakerModel
from app.models.track import Track as TrackModel
from .helpers import custom_fields as fields
from .helpers.helpers import (
    can_create,
    can_update,
    can_delete
)
from .helpers.helpers import save_db_model, get_object_in_event, \
    model_custom_form, requires_auth, parse_args
from .helpers.special_fields import SessionLanguageField, SessionStateField
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, SERVICE_RESPONSES
from .helpers.utils import Resource, ETAG_HEADER_DEFN

api = Namespace('sessions', description='Sessions', path='/')

# Create models
SESSION_TRACK = api.model('SessionTrack', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'color': fields.Color(),
})

SESSION_SPEAKER = api.model('SessionSpeaker', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'organisation': fields.String(),
    'city': fields.String(),
    'heard_from': fields.String(),
    'speaking_experience': fields.String(),
    'sponsorship_required': fields.String()
})

SESSION_MICROLOCATION = api.model('SessionMicrolocation', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
})

SESSION_TYPE = api.model('SessionType', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'length': fields.String(required=True)
})

SESSION_TYPE_POST = api.clone('SessionTypePost', SESSION_TYPE)
del SESSION_TYPE_POST['id']

SESSION = api.model('Session', {
    'id': fields.Integer(required=True),
    'title': fields.String(required=True),
    'subtitle': fields.String(),
    'level': fields.String(),
    'short_abstract': fields.String(),
    'long_abstract': fields.String(),
    'comments': fields.String(),
    'start_time': fields.DateTime(required=True),
    'end_time': fields.DateTime(required=True),
    'track': fields.Nested(SESSION_TRACK, allow_null=True),
    'speakers': fields.List(fields.Nested(SESSION_SPEAKER)),
    'language': SessionLanguageField(),
    'microlocation': fields.Nested(SESSION_MICROLOCATION, allow_null=True),
    'slides': fields.Upload(),
    'video': fields.Upload(),
    'audio': fields.Upload(),
    'signup_url': fields.Uri(),
    'state': SessionStateField(),
    'session_type': fields.Nested(SESSION_TYPE, allow_null=True)
})

SESSION_PAGINATED = api.clone('SessionPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SESSION))
})

SESSION_POST = api.clone('SessionPost', SESSION, {
    'track_id': fields.Integer(),
    'speaker_ids': fields.List(fields.Integer()),
    'microlocation_id': fields.Integer(),
    'session_type_id': fields.Integer()
})

del SESSION_POST['id']
del SESSION_POST['track']
del SESSION_POST['speakers']
del SESSION_POST['microlocation']
del SESSION_POST['session_type']


# Create DAO

class SessionTypeDAO(ServiceDAO):
    """
    SessionType DAO
    added for import/export feature
    """
    version_key = 'sessions_ver'


class SessionDAO(ServiceDAO):
    version_key = 'sessions_ver'

    def _delete_fields(self, data):
        data = self._del(data, ['speaker_ids', 'track_id',
                                'microlocation_id', 'session_type_id'])
        # convert datetime fields
        for _ in ['start_time', 'end_time']:
            if _ in data:
                data[_] = SESSION_POST[_].from_str(data[_])
        return data

    def get_object(self, model, sid, event_id):
        """
        returns object (model). Checks if object is in same event
        """
        if sid is None:
            return None
        return get_object_in_event(model, sid, event_id)

    def fix_payload_post(self, event_id, data):
        """
        Fixes payload of POST request
        """
        if 'track_id' in data:
            data['track'] = self.get_object(
                TrackModel, data.get('track_id'), event_id)
        if 'microlocation_id' in data:
            data['microlocation'] = self.get_object(
                MicrolocationModel, data.get('microlocation_id'), event_id)
        if 'session_type_id' in data:
            data['session_type'] = self.get_object(
                SessionTypeModel, data.get('session_type_id'), event_id)
        if 'speaker_ids' in data:
            data['speakers'] = InstrumentedList(
                SpeakerModel.query.get(_) for _ in data.get('speaker_ids', [])
                if self.get_object(SpeakerModel, _, event_id) is not None
            )
        data['event_id'] = event_id
        data = self._delete_fields(data)
        return data

    def update(self, event_id, service_id, data):
        data = self.validate(data, event_id, check_required=False)
        data_copy = data.copy()
        data_copy = self.fix_payload_post(event_id, data_copy)
        data = self._delete_fields(data)
        session = DataGetter.get_session(service_id)  # session before any updates are made
        obj = ServiceDAO.update(self, event_id, service_id, data, validate=False)  # session after update

        if 'state' in data:
            if data['state'] == 'pending' and session.state == 'draft':
                trigger_new_session_notifications(session.id, event_id=event_id)

            if (data['state'] == 'accepted' and session.state != 'accepted') \
                or (data['state'] == 'rejected' and session.state != 'rejected'):
                trigger_session_state_change_notifications(obj, event_id=event_id, state=data['state'])

        if session.start_time != obj.start_time or session.end_time != obj.end_time:
            trigger_session_schedule_change_notifications(obj, event_id)

        for f in ['track', 'microlocation', 'speakers', 'session_type']:
            if f in data_copy:
                setattr(obj, f, data_copy[f])
        obj = save_db_model(obj, SessionModel.__name__, event_id)
        return obj

    def create(self, event_id, data, url):
        data = self.validate(data, event_id)
        payload = self.fix_payload_post(event_id, data)
        speakers = payload.pop('speakers', None)
        session, status_code, location = ServiceDAO.create(self, event_id, payload, url, validate=False)
        if speakers:
            session.speakers = speakers
            save_to_db(session)
        if not self.is_importing and session.state == 'pending':
            trigger_new_session_notifications(session.id, event_id=event_id)
        return session, status_code, location

    def validate(self, data, event_id, check_required=True):
        form = DataGetter.get_custom_form_elements(event_id)
        model = None
        if form:
            model = model_custom_form(form.session_form, self.post_api_model)
        return ServiceDAO.validate(
            self, data, model=model, check_required=check_required)


DAO = SessionDAO(SessionModel, SESSION_POST)
TypeDAO = SessionTypeDAO(SessionTypeModel, SESSION_TYPE_POST)

# Define Params

SESSIONS_PARAMS = {
    'start_time_gt': {},
    'start_time_lt': {},
    'end_time_gt': {},
    'end_time_lt': {},
    'order_by': {
        'description': 'Order by a field, example "start_time.asc" or "end_time.desc"'
    }
}


# #########
# Resources
# #########


class SessionResource():
    """
    Session Resource Base class
    """
    session_parser = reqparse.RequestParser()
    session_parser.add_argument('start_time_gt', dest='__sessions_start_time_gt')
    session_parser.add_argument('start_time_lt', dest='__sessions_start_time_lt')
    session_parser.add_argument('end_time_gt', dest='__sessions_end_time_gt')
    session_parser.add_argument('end_time_lt', dest='__sessions_end_time_lt')
    session_parser.add_argument('order_by', dest='__sessions_order_by')


@api.route('/events/<int:event_id>/sessions/<int:session_id>')
@api.doc(responses=SERVICE_RESPONSES)
class Session(Resource):
    @api.doc('get_session')
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_with(SESSION)
    def get(self, event_id, session_id):
        """Fetch a session given its id"""
        return DAO.get(event_id, session_id)

    @requires_auth
    @can_delete(DAO)
    @api.doc('delete_session')
    @api.marshal_with(SESSION)
    def delete(self, event_id, session_id):
        """Delete a session given its id"""
        return DAO.delete(event_id, session_id)

    @requires_auth
    @can_update(DAO)
    @api.doc('update_session', responses=PUT_RESPONSES)
    @api.marshal_with(SESSION)
    @api.expect(SESSION_POST)
    def put(self, event_id, session_id):
        """Update a session given its id"""
        return DAO.update(event_id, session_id, self.api.payload)


@api.route('/events/<int:event_id>/sessions')
class SessionList(Resource, SessionResource):
    @api.doc('list_sessions', params=SESSIONS_PARAMS)
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_list_with(SESSION)
    def get(self, event_id):
        """List all sessions"""
        return DAO.list(event_id, **parse_args(self.session_parser))

    @requires_auth
    @can_create(DAO)
    @api.doc('create_session', responses=POST_RESPONSES)
    @api.marshal_with(SESSION)
    @api.expect(SESSION_POST)
    def post(self, event_id):
        """Create a session"""
        item = DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )
        record_activity('create_session', session=item[0], event_id=event_id)
        return item


@api.route('/events/<int:event_id>/sessions/page')
class SessionListPaginated(Resource, PaginatedResourceBase, SessionResource):
    @api.doc('list_sessions_paginated', params=PAGE_PARAMS)
    @api.doc(params=SESSIONS_PARAMS)
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_with(SESSION_PAGINATED)
    def get(self, event_id):
        """List sessions in a paginated manner"""
        args = self.parser.parse_args()
        return DAO.paginated_list(
            args=args, event_id=event_id, **parse_args(self.session_parser)
        )


# Use Session DAO to check for permission

@api.route('/events/<int:event_id>/sessions/types')
class SessionTypeList(Resource):
    @api.doc('list_session_types')
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_list_with(SESSION_TYPE)
    def get(self, event_id):
        """List all session types"""
        return TypeDAO.list(event_id)

    @requires_auth
    @can_create(DAO)
    @api.doc('create_session_type', responses=POST_RESPONSES)
    @api.marshal_with(SESSION_TYPE)
    @api.expect(SESSION_TYPE_POST)
    def post(self, event_id):
        """Create a session type"""
        return TypeDAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )


@api.route('/events/<int:event_id>/sessions/types/<int:type_id>')
class SessionType(Resource):
    @requires_auth
    @can_delete(DAO)
    @api.doc('delete_session_type')
    @api.marshal_with(SESSION_TYPE)
    def delete(self, event_id, type_id):
        """Delete a session type given its id"""
        return TypeDAO.delete(event_id, type_id)

    @requires_auth
    @can_update(DAO)
    @api.doc('update_session_type', responses=PUT_RESPONSES)
    @api.marshal_with(SESSION_TYPE)
    @api.expect(SESSION_TYPE_POST)
    def put(self, event_id, type_id):
        """Update a session type given its id"""
        return TypeDAO.update(event_id, type_id, self.api.payload)

    @api.hide
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_with(SESSION_TYPE)
    def get(self, event_id, type_id):
        """Fetch a session type given its id"""
        return TypeDAO.get(event_id, type_id)

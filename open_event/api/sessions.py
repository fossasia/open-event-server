from flask.ext.restplus import Resource, Namespace
from sqlalchemy.orm.collections import InstrumentedList

from open_event.models.session import Session as SessionModel, \
    Language as LanguageModel, Level as LevelModel
from open_event.models.track import Track as TrackModel
from open_event.models.microlocation import Microlocation as MicrolocationModel
from open_event.models.speaker import Speaker as SpeakerModel

from .helpers.helpers import get_paginated_list, requires_auth, \
    save_db_model, get_object_in_event
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('sessions', description='Sessions', path='/')

# Create models
SESSION_TRACK = api.model('SessionTrack', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
})

SESSION_SPEAKER = api.model('SessionSpeaker', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
})

SESSION_LEVEL = api.model('SessionLevel', {
    'id': fields.Integer(required=True),
    'label_en': fields.String(),
})

SESSION_LANGUAGE = api.model('SessionLanguage', {
    'id': fields.Integer(required=True),
    'label_en': fields.String(),
    'label_de': fields.String(),
})

SESSION_MICROLOCATION = api.model('SessionMicrolocation', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
})

SESSION = api.model('Session', {
    'id': fields.Integer(required=True),
    'title': fields.String(),
    'subtitle': fields.String(),
    'abstract': fields.String(),
    'description': fields.String(),
    'start_time': fields.DateTime(),
    'end_time': fields.DateTime(),
    'track': fields.Nested(SESSION_TRACK),
    'speakers': fields.List(fields.Nested(SESSION_SPEAKER)),
    'level': fields.Nested(SESSION_LEVEL),
    'language': fields.Nested(SESSION_LANGUAGE),
    'microlocation': fields.Nested(SESSION_MICROLOCATION),
    'slides': fields.String(),
    'video': fields.String(),
    'audio': fields.String(),
    'signup_url': fields.Uri()
})

SESSION_PAGINATED = api.clone('SessionPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SESSION))
})

SESSION_POST = api.clone('SessionPost', SESSION, {
    'track_id': fields.Integer(),
    'speaker_ids': fields.List(fields.Integer()),
    'level_id': fields.Integer(),
    'language_id': fields.Integer(),
    'microlocation_id': fields.Integer()
})
del SESSION_POST['id']
del SESSION_POST['track']
del SESSION_POST['speakers']
del SESSION_POST['level']
del SESSION_POST['language']
del SESSION_POST['microlocation']


# Create DAO
class SessionDAO(ServiceDAO):
    def _delete_fields(self, data):
        del data['speaker_ids']
        del data['track_id']
        del data['level_id']
        del data['language_id']
        del data['microlocation_id']
        data['start_time'] = SESSION_POST['start_time'].from_str(
            data['start_time'])
        data['end_time'] = SESSION_POST['end_time'].from_str(data['end_time'])
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
        data['track'] = self.get_object(TrackModel, data['track_id'], event_id)
        data['level'] = self.get_object(LevelModel, data['level_id'], event_id)
        data['language'] = self.get_object(LanguageModel, data['language_id'], event_id)
        data['microlocation'] = self.get_object(MicrolocationModel, data['microlocation_id'], event_id)
        data['event_id'] = event_id
        data['speakers'] = InstrumentedList(
            SpeakerModel.query.get(_) for _ in data['speaker_ids']
            if self.get_object(SpeakerModel, _, event_id) is not None
        )
        data = self._delete_fields(data)
        return data

    def update(self, event_id, service_id, data):
        self.validate(data)
        data_copy = data.copy()
        data_copy = self.fix_payload_post(event_id, data_copy)
        data = self._delete_fields(data)
        obj = ServiceDAO.update(self, event_id, service_id, data)
        obj.track = data_copy['track']
        obj.level = data_copy['level']
        obj.language = data_copy['language']
        obj.microlocation = data_copy['microlocation']
        obj.speakers = data_copy['speakers']
        obj = save_db_model(obj, SessionModel.__name__, event_id)
        return obj

    def create(self, event_id, data, url):
        self.validate(data)
        payload = self.fix_payload_post(event_id, data)
        return ServiceDAO.create(self, event_id, payload, url, validate=False)


DAO = SessionDAO(SessionModel, SESSION_POST)


@api.route('/events/<int:event_id>/sessions/<int:session_id>')
@api.response(404, 'Session not found')
@api.response(400, 'Session does not belong to event')
class Session(Resource):
    @api.doc('get_session')
    @api.marshal_with(SESSION)
    def get(self, event_id, session_id):
        """Fetch a session given its id"""
        return DAO.get(event_id, session_id)

    @requires_auth
    @api.doc('delete_session')
    @api.marshal_with(SESSION)
    def delete(self, event_id, session_id):
        """Delete a session given its id"""
        return DAO.delete(event_id, session_id)

    @requires_auth
    @api.doc('update_session', responses=PUT_RESPONSES)
    @api.marshal_with(SESSION)
    @api.expect(SESSION_POST)
    def put(self, event_id, session_id):
        """Update a session given its id"""
        return DAO.update(event_id, session_id, self.api.payload)


@api.route('/events/<int:event_id>/sessions')
class SessionList(Resource):
    @api.doc('list_sessions')
    @api.marshal_list_with(SESSION)
    def get(self, event_id):
        """List all sessions"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_session', responses=POST_RESPONSES)
    @api.marshal_with(SESSION)
    @api.expect(SESSION_POST)
    def post(self, event_id):
        """Create a session"""
        return DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )

@api.route('/events/<int:event_id>/sessions/page')
class SessionListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_sessions_paginated', params=PAGE_PARAMS)
    @api.marshal_with(SESSION_PAGINATED)
    def get(self, event_id):
        """List sessions in a paginated manner"""
        return get_paginated_list(
            SessionModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Session as SessionModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event,\
    get_paginated_list
from utils import PAGINATED_MODEL, PaginatedResourceBase

api = Namespace('sessions', description='Sessions', path='/')

SESSION_TRACK = api.model('SessionTrack', {
    'id': fields.Integer(required=True),
    'name': fields.String,
})

SESSION_SPEAKER = api.model('SessionSpeaker', {
    'id': fields.Integer(required=True),
    'name': fields.String,
})

SESSION_LEVEL = api.model('SessionLevel', {
    'id': fields.Integer(required=True),
    'label_en': fields.String,
})

SESSION_LANGUAGE = api.model('SessionLanguage', {
    'id': fields.Integer(required=True),
    'label_en': fields.String,
    'label_de': fields.String,
})

SESSION_FORMAT = api.model('SessionFormat', {
    'id': fields.Integer(required=True),
    'name': fields.String
})

SESSION_MICROLOCATION = api.model('SessionMicrolocation', {
    'id': fields.Integer(required=True),
    'name': fields.String,
})

SESSION = api.model('Session', {
    'id': fields.Integer(required=True),
    'title': fields.String,
    'subtitle': fields.String,
    'abstract': fields.String,
    'description': fields.String,
    'start_time': fields.DateTime,
    'end_time': fields.DateTime,
    'track': fields.Nested(SESSION_TRACK),
    'speakers': fields.List(fields.Nested(SESSION_SPEAKER)),
    'level': fields.Nested(SESSION_LEVEL),
    'language': fields.Nested(SESSION_LANGUAGE),
    'format': fields.Nested(SESSION_FORMAT),
    'microlocation': fields.Nested(SESSION_MICROLOCATION),
})

SESSION_PAGINATED = api.clone('SessionPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SESSION))
})


@api.route('/events/<int:event_id>/sessions/<int:session_id>')
@api.response(404, 'Session not found')
@api.response(400, 'Object does not belong to event')
class Session(Resource):
    @api.doc('get_session')
    @api.marshal_with(SESSION)
    def get(self, event_id, session_id):
        """Fetch a session given its id"""
        return get_object_in_event(SessionModel, session_id, event_id)


@api.route('/events/<int:event_id>/sessions')
@api.param('event_id')
class SessionList(Resource):
    @api.doc('list_sessions')
    @api.marshal_list_with(SESSION)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(SessionModel, event_id=event_id)


@api.route('/events/<int:event_id>/sessions/page')
class SessionListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_sessions_paginated')
    @api.param('start')
    @api.param('limit')
    @api.marshal_with(SESSION_PAGINATED)
    def get(self, event_id):
        """List sessions in a paginated manner"""
        return get_paginated_list(
            SessionModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

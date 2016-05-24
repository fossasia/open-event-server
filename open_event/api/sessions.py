from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Session as SessionModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('sessions', description='Sessions', path='/')

TRACK = api.model('Track', {
    'id': fields.Integer(required=True),
    'name': fields.String,
})

SPEAKER = api.model('Speaker', {
    'id': fields.Integer(required=True),
    'name': fields.String,
})

LEVEL = api.model('Level', {
    'id': fields.Integer(required=True),
    'label_en': fields.String,
})

LANGUAGE = api.model('Language', {
    'id': fields.Integer(required=True),
    'label_en': fields.String,
    'label_de': fields.String,
})

MICROLOCATION = api.model('Microlocation', {
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
    'track': fields.Nested(TRACK),
    'speakers': fields.List(fields.Nested(SPEAKER)),
    'level': fields.Nested(LEVEL),
    'language': fields.Nested(LANGUAGE),
    'microlocation': fields.Nested(MICROLOCATION),
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

from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404

api = Namespace('events', description='Events')

event = api.model('Event', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'email': fields.String,
    'color': fields.String,
    'logo': fields.String,
    'start_time': fields.DateTime,
    'end_time': fields.DateTime,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'slogan': fields.String,
    'url': fields.String,
    'location_name': fields.String,
})


@api.route('/<int:id>')
@api.param('id')
@api.response(404, 'Event not found')
class Event(Resource):
    @api.doc('get_event')
    @api.marshal_with(event)
    def get(self, id):
        """Fetch an event given its id"""
        return get_object_or_404(EventModel, id)


@api.route('/')
class EventList(Resource):
    @api.doc('list_events')
    @api.marshal_list_with(event)
    def get(self):
        """List all events"""
        return get_object_list(EventModel)

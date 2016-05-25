from flask.ext.restplus import Resource, Namespace, fields, reqparse

from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_paged_object
from utils import PAGED_MODEL, PAGE_REQPARSER


api = Namespace('events', description='Events')

EVENT = api.model('Event', {
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

EVENT_PAGED = api.clone('EventPaged', PAGED_MODEL, {
    'results': fields.List(fields.Nested(EVENT))
})


@api.route('/<int:event_id>')
@api.param('event_id')
@api.response(404, 'Event not found')
class Event(Resource):
    @api.doc('get_event')
    @api.marshal_with(EVENT)
    def get(self, event_id):
        """Fetch an event given its id"""
        return get_object_or_404(EventModel, event_id)


@api.route('/')
class EventList(Resource):
    @api.doc('list_events')
    @api.marshal_list_with(EVENT)
    def get(self):
        """List all events"""
        return get_object_list(EventModel)


@api.route('/page')
class EventListPaged(Resource):
    parser = PAGE_REQPARSER

    @api.doc('list_events_paged', params={
        'start': 'Position to start from',
        'limit': 'Max items to return'
    })
    @api.marshal_with(EVENT_PAGED)
    def get(self):
        """List events in paged form"""
        args = self.parser.parse_args()
        url = self.api.url_for(self)  # WARN: undocumented way
        return get_paged_object(EventModel, url, args=args)

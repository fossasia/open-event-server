from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_paginated_list
from utils import PAGINATED_MODEL, PaginatedResourceBase
from custom_fields import EmailField

api = Namespace('events', description='Events')

EVENT = api.model('Event', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'email': EmailField,
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

EVENT_PAGINATED = api.clone('EventPaginated', PAGINATED_MODEL, {
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


@api.route('')
class EventList(Resource):
    @api.doc('list_events')
    @api.marshal_list_with(EVENT)
    def get(self):
        """List all events"""
        return get_object_list(EventModel)


@api.route('/page')
class EventListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_events_paginated')
    @api.param('start')
    @api.param('limit')
    @api.marshal_with(EVENT_PAGINATED)
    def get(self):
        """List events in a paginated manner"""
        args = self.parser.parse_args()
        url = self.api.url_for(self)  # WARN: undocumented way
        return get_paginated_list(EventModel, url, args=args)

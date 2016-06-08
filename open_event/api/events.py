from flask.ext.restplus import Resource, Namespace, fields
from flask import g

from custom_fields import EmailField, ColorField, UriField, ImageUriField
from open_event.models.event import Event as EventModel, EventsUsers
from open_event.models.user import ADMIN, SUPERADMIN
from .helpers import get_object_list, get_object_or_404, get_paginated_list,\
    requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, PAGE_PARAMS, POST_RESPONSES
from open_event.helpers.data import save_to_db, update_version, delete_from_db

api = Namespace('events', description='Events')

EVENT = api.model('Event', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'email': EmailField(),
    'color': ColorField(),
    'logo': ImageUriField(),
    'start_time': fields.DateTime,
    'end_time': fields.DateTime,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'event_url': UriField(),
    'background_url': UriField(),
    'description': fields.String,
    'location_name': fields.String,
    'state': fields.String,
    'closing_date': fields.DateTime,
})

EVENT_PAGINATED = api.clone('EventPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(EVENT))
})

EVENT_POST = api.clone('EventPost', EVENT)
del EVENT_POST['id']


@api.route('/<int:event_id>')
@api.param('event_id')
@api.response(404, 'Event not found')
class Event(Resource):
    @api.doc('get_event')
    @api.marshal_with(EVENT)
    def get(self, event_id):
        """Fetch an event given its id"""
        return get_object_or_404(EventModel, event_id)

    @requires_auth
    @api.doc('delete_event')
    @api.marshal_with(EVENT)
    def delete(self, event_id):
        """Delete an event given its id"""
        event = get_object_or_404(EventModel, event_id)
        delete_from_db(event, 'Event deleted')
        return event


@api.route('')
class EventList(Resource):
    @api.doc('list_events')
    @api.marshal_list_with(EVENT)
    def get(self):
        """List all events"""
        return get_object_list(EventModel)

    @requires_auth
    @api.doc('create_event', responses=POST_RESPONSES)
    @api.marshal_with(EVENT)
    @api.expect(EVENT_POST, validate=True)
    def post(self):
        """Create an event"""
        new_event = EventModel(**self.api.payload)
        a = EventsUsers()
        a.user = g.user
        a.editor = True
        a.admin = True
        a.role = SUPERADMIN if a.user.role == SUPERADMIN else ADMIN
        new_event.users.append(a)
        save_to_db(new_event, "Event saved")
        update_version(
            event_id=new_event.id,
            is_created=True,
            column_to_increment="event_ver"
        )
        # return the new event created
        return get_object_or_404(EventModel, new_event.id)


@api.route('/page')
class EventListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_events_paginated', params=PAGE_PARAMS)
    @api.marshal_with(EVENT_PAGINATED)
    def get(self):
        """List events in a paginated manner"""
        args = self.parser.parse_args()
        url = self.api.url_for(self)  # WARN: undocumented way
        return get_paginated_list(EventModel, url, args=args)

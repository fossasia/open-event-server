from flask.ext.restplus import Resource, Namespace
from flask import g

from open_event.models.event import Event as EventModel, EventsUsers
from open_event.helpers.data import save_to_db, update_version

from .helpers.helpers import get_paginated_list, requires_auth
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, BaseDAO
from .helpers import custom_fields as fields
from helpers.special_fields import EventTypeField, EventTopicField


api = Namespace('events', description='Events')

EVENT = api.model('Event', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'email': fields.Email(),
    'color': fields.Color(),
    'logo': fields.ImageUri(),
    'start_time': fields.DateTime(required=True),
    'end_time': fields.DateTime(required=True),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'event_url': fields.Uri(),
    'background_url': fields.ImageUri(),
    'description': fields.String(),
    'location_name': fields.String(),
    'organizer_name': fields.String(),
    'organizer_description': fields.String(),
    'state': fields.String(),
    'closing_datetime': fields.DateTime(),
    'type': EventTypeField(),
    'topic': EventTopicField(),
    'privacy': fields.String(),
    'ticket_url': fields.Uri()
})

EVENT_PAGINATED = api.clone('EventPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(EVENT))
})

EVENT_POST = api.clone('EventPost', EVENT)
del EVENT_POST['id']


class EventDAO(BaseDAO):
    """
    Event DAO
    """
    def fix_payload(self, data):
        """
        Fixes the payload data.
        Here converts string time from datetime obj
        """
        data['start_time'] = EVENT_POST['start_time'].from_str(data['start_time'])
        data['end_time'] = EVENT_POST['end_time'].from_str(data['end_time'])
        data['closing_datetime'] = EVENT_POST['closing_datetime'].from_str(
            data['closing_datetime'])
        return data

    def create(self, data, url):
        self.validate(data)
        payload = self.fix_payload(data)
        new_event = self.model(**payload)
        # set user (owner)
        a = EventsUsers()
        a.user = g.user
        a.editor = True
        a.admin = True
        new_event.users.append(a)
        save_to_db(new_event, "Event saved")
        update_version(
            event_id=new_event.id,
            is_created=True,
            column_to_increment="event_ver"
        )

        # Return created resource with a 201 status code and its Location
        # (url) in the header.
        resource_location = url + '/' + str(new_event.id)
        return self.get(new_event.id), 201, {'Location': resource_location}

    def update(self, event_id, data):
        self.validate(data)
        payload = self.fix_payload(data)
        return BaseDAO.update(self, event_id, payload, validate=False)


DAO = EventDAO(EventModel, EVENT_POST)


@api.route('/<int:event_id>')
@api.param('event_id')
@api.response(404, 'Event not found')
class Event(Resource):
    @api.doc('get_event')
    @api.marshal_with(EVENT)
    def get(self, event_id):
        """Fetch an event given its id"""
        return DAO.get(event_id)

    @requires_auth
    @api.doc('delete_event')
    @api.marshal_with(EVENT)
    def delete(self, event_id):
        """Delete an event given its id"""
        return DAO.delete(event_id)

    @requires_auth
    @api.doc('update_event', responses=PUT_RESPONSES)
    @api.marshal_with(EVENT)
    @api.expect(EVENT_POST)
    def put(self, event_id):
        """Update a event given its id"""
        return DAO.update(event_id, self.api.payload)


@api.route('')
class EventList(Resource):
    @api.doc('list_events')
    @api.marshal_list_with(EVENT)
    def get(self):
        """List all events"""
        return DAO.list()

    @requires_auth
    @api.doc('create_event', responses=POST_RESPONSES)
    @api.marshal_with(EVENT)
    @api.expect(EVENT_POST)
    def post(self):
        """Create an event"""
        return DAO.create(self.api.payload, self.api.url_for(self))


@api.route('/page')
class EventListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_events_paginated', params=PAGE_PARAMS)
    @api.marshal_with(EVENT_PAGINATED)
    def get(self):
        """List events in a paginated manner"""
        args = self.parser.parse_args()
        url = self.api.url_for(self)  # WARN: undocumented way
        return get_paginated_list(EventModel, url, args=args)

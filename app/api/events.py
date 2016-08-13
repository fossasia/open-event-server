from flask.ext.restplus import Namespace, reqparse, marshal
from flask import g

from app.api.microlocations import MICROLOCATION
from app.api.sessions import SESSION
from app.api.speakers import SPEAKER
from app.api.sponsors import SPONSOR
from app.api.tracks import TRACK
from app.models.event import Event as EventModel
from app.models.social_link import SocialLink as SocialLinkModel
from app.models.users_events_roles import UsersEventsRoles
from app.models.event_copyright import EventCopyright
from app.models.call_for_papers import CallForPaper as EventCFS
from app.models.role import Role
from app.models.user import ORGANIZER
from app.helpers.data import save_to_db, record_activity

from .helpers.helpers import requires_auth, parse_args, \
    can_access, fake_marshal_with, fake_marshal_list_with, erase_from_dict
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, BaseDAO, ServiceDAO
from .helpers.utils import Resource, ETAG_HEADER_DEFN
from .helpers import custom_fields as fields
from helpers.special_fields import EventTypeField, EventTopicField, \
    EventPrivacyField, EventSubTopicField, EventStateField

api = Namespace('events', description='Events')

EVENT_CREATOR = api.model('EventCreator', {
    'id': fields.Integer(),
    'email': fields.Email()
})

EVENT_COPYRIGHT = api.model('EventCopyright', {
    'holder': fields.String(),
    'holder_url': fields.Uri(),
    'licence': fields.String(),
    'licence_url': fields.Uri(),
    'year': fields.Integer(),
    'logo': fields.String()
})

EVENT_CFS = api.model('EventCFS', {
    'announcement': fields.String(),
    'start_date': fields.DateTime(),
    'end_date': fields.DateTime(),
    'timezone': fields.String(),
    'privacy': EventPrivacyField()  # [public, private]
})

EVENT_VERSION = api.model('EventVersion', {
    'event_ver': fields.Integer(),
    'sessions_ver': fields.Integer(),
    'speakers_ver': fields.Integer(),
    'tracks_ver': fields.Integer(),
    'sponsors_ver': fields.Integer(),
    'microlocations_ver': fields.Integer()
})

SOCIAL_LINK = api.model('SocialLink', {
    'id': fields.Integer(),
    'name': fields.String(required=True),
    'link': fields.String(required=True)
})

SOCIAL_LINK_POST = api.clone('SocialLinkPost', SOCIAL_LINK)
del SOCIAL_LINK_POST['id']

EVENT = api.model('Event', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'event_url': fields.Uri(),
    'email': fields.Email(),
    'logo': fields.Upload(),
    'start_time': fields.DateTime(required=True),
    'end_time': fields.DateTime(required=True),
    'timezone': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'background_image': fields.Upload(attribute='background_url'),
    'description': fields.String(),
    'location_name': fields.String(),
    'searchable_location_name': fields.String(),
    'organizer_name': fields.String(),
    'organizer_description': fields.String(),
    'state': EventStateField(default='Draft'),
    'type': EventTypeField(),
    'topic': EventTopicField(),
    'sub_topic': EventSubTopicField(),
    'privacy': EventPrivacyField(),
    'ticket_url': fields.Uri(),
    'creator': fields.Nested(EVENT_CREATOR, allow_null=True),
    'copyright': fields.Nested(EVENT_COPYRIGHT, allow_null=True),
    'schedule_published_on': fields.DateTime(),
    'code_of_conduct': fields.String(),
    'social_links': fields.List(fields.Nested(SOCIAL_LINK), attribute='social_link'),
    'call_for_papers': fields.Nested(EVENT_CFS, allow_null=True),
    'version': fields.Nested(EVENT_VERSION)
})

EVENT_COMPLETE = api.clone('EventComplete', EVENT, {
    'sessions': fields.List(fields.Nested(SESSION), attribute='session'),
    'microlocations': fields.List(fields.Nested(MICROLOCATION), attribute='microlocation'),
    'tracks': fields.List(fields.Nested(TRACK), attribute='track'),
    'sponsors': fields.List(fields.Nested(SPONSOR), attribute='sponsor'),
    'speakers': fields.List(fields.Nested(SPEAKER), attribute='speaker'),
})

EVENT_PAGINATED = api.clone('EventPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(EVENT))
})

EVENT_POST = api.clone('EventPost', EVENT)
del EVENT_POST['id']
del EVENT_POST['creator']
del EVENT_POST['social_links']
del EVENT_POST['version']


# ###################
# Data Access Objects
# ###################


class SocialLinkDAO(ServiceDAO):
    """
    Social Link DAO
    """
    version_key = 'event_ver'


class EventDAO(BaseDAO):
    """
    Event DAO
    """
    version_key = 'event_ver'

    def fix_payload(self, data):
        """
        Fixes the payload data.
        Here converts string time from datetime obj
        """
        datetime_fields = ['start_time', 'end_time', 'schedule_published_on']
        for f in datetime_fields:
            if f in data:
                data[f] = EVENT_POST[f].from_str(data.get(f))
        # cfs datetimes
        if data.get('call_for_papers'):
            for _ in ['start_date', 'end_date']:
                if _ in data['call_for_papers']:
                    data['call_for_papers'][_] = EVENT_CFS[_].from_str(
                        data['call_for_papers'].get(_))
        return data

    def create(self, data, url):
        data = self.validate(data)
        payload = self.fix_payload(data)
        # save copyright info
        payload['copyright'] = CopyrightDAO.create(payload.get('copyright', {}), validate=False)
        # save cfs info
        if payload.get('call_for_papers'):  # don't create if call_for_papers==null
            payload['call_for_papers'] = CFSDAO.create(payload['call_for_papers'], validate=False)
        # save event
        new_event = self.model(**payload)
        new_event.creator = g.user
        save_to_db(new_event, "Event saved")
        # set organizer
        role = Role.query.filter_by(name=ORGANIZER).first()
        uer = UsersEventsRoles(g.user, new_event, role)
        save_to_db(uer, 'UER saved')
        # Return created resource with a 201 status code and its Location
        # (url) in the header.
        resource_location = url + '/' + str(new_event.id)
        return self.get(new_event.id), 201, {'Location': resource_location}

    def update(self, event_id, data):
        data = self.validate_put(data)
        payload = self.fix_payload(data)
        # get event
        event = self.get(event_id)
        # update copyright if key exists
        if 'copyright' in payload:
            CopyrightDAO.update(event.copyright.id, payload['copyright']
                                if payload['copyright'] else {})
            payload.pop('copyright')
        # update cfs
        if 'call_for_papers' in payload:
            cfs_data = payload.get('call_for_papers')
            if event.call_for_papers:
                if cfs_data:  # update existing
                    CFSDAO.update(event.call_for_papers.id, cfs_data)
                else:  # delete if null
                    CFSDAO.delete(event.call_for_papers.id)
            elif cfs_data:  # create new (only if data exists)
                CFSDAO.create(cfs_data, validate=False)
            payload.pop('call_for_papers')
        # master update
        return BaseDAO.update(self, event_id, payload, validate=False)


LinkDAO = SocialLinkDAO(SocialLinkModel, SOCIAL_LINK_POST)
DAO = EventDAO(EventModel, EVENT_POST)
CopyrightDAO = BaseDAO(EventCopyright, EVENT_COPYRIGHT)
CFSDAO = BaseDAO(EventCFS, EVENT_CFS)  # CFS = Call For Speakers

# DEFINE PARAMS

EVENT_PARAMS = {
    'location': {},
    'contains': {
        'description': 'Contains the string in name and description'
    },
    'state': {},
    'privacy': {},
    'type': {},
    'topic': {},
    'sub_topic': {},
    'start_time_gt': {},
    'start_time_lt': {},
    'end_time_gt': {},
    'end_time_lt': {},
    'time_period': {},
    'include': {
        'description': 'Comma separated list of additional fields to load. '
                       'Supported: sessions,tracks,microlocations,speakers,sponsors)'
    },
}

SINGLE_EVENT_PARAMS = {
    'include': {
        'description': 'Comma separated list of additional fields to load. '
                       'Supported: sessions,tracks,microlocations,speakers,sponsors)'
    },
}


def get_extended_event_model(includes=None):
    if includes is None:
        includes = []
    included_fields = {}
    if 'sessions' in includes:
        included_fields['sessions'] = fields.List(fields.Nested(SESSION), attribute='session')
    if 'tracks' in includes:
        included_fields['tracks'] = fields.List(fields.Nested(TRACK), attribute='track')
    if 'microlocations' in includes:
        included_fields['microlocations'] = fields.List(fields.Nested(MICROLOCATION), attribute='microlocation')
    if 'sponsors' in includes:
        included_fields['sponsors'] = fields.List(fields.Nested(SPONSOR), attribute='sponsor')
    if 'speakers' in includes:
        included_fields['speakers'] = fields.List(fields.Nested(SPEAKER), attribute='speaker')
    return EVENT.extend('ExtendedEvent', included_fields)

# DEFINE RESOURCES


class EventResource():
    """
    Event Resource Base class
    """
    event_parser = reqparse.RequestParser()
    event_parser.add_argument('location', type=unicode, dest='__event_search_location')
    event_parser.add_argument('contains', type=unicode, dest='__event_contains')
    event_parser.add_argument('state', type=str)
    event_parser.add_argument('privacy', type=str)
    event_parser.add_argument('type', type=str)
    event_parser.add_argument('topic', type=str)
    event_parser.add_argument('sub_topic', type=str)
    event_parser.add_argument('start_time_gt', dest='__event_start_time_gt')
    event_parser.add_argument('start_time_lt', dest='__event_start_time_lt')
    event_parser.add_argument('end_time_gt', dest='__event_end_time_gt')
    event_parser.add_argument('end_time_lt', dest='__event_end_time_lt')
    event_parser.add_argument('time_period', type=str, dest='__event_time_period')
    event_parser.add_argument('include', type=str)


class SingleEventResource():
    event_parser = reqparse.RequestParser()
    event_parser.add_argument('include', type=str)


@api.route('/<int:event_id>')
@api.param('event_id')
@api.response(404, 'Event not found')
class Event(Resource, SingleEventResource):
    @api.doc('get_event', params=SINGLE_EVENT_PARAMS)
    @api.header(*ETAG_HEADER_DEFN)
    @fake_marshal_with(EVENT_COMPLETE)  # Fake marshal decorator to add response model to swagger doc
    def get(self, event_id):
        """Fetch an event given its id"""
        includes = parse_args(self.event_parser).get('include', '').split(',')
        return marshal(DAO.get(event_id), get_extended_event_model(includes))

    @requires_auth
    @can_access
    @api.doc('delete_event')
    @api.marshal_with(EVENT)
    def delete(self, event_id):
        """Delete an event given its id"""
        event = DAO.delete(event_id)
        record_activity('delete_event', event_id=event_id)
        return event

    @requires_auth
    @can_access
    @api.doc('update_event', responses=PUT_RESPONSES)
    @api.marshal_with(EVENT)
    @api.expect(EVENT_POST)
    def put(self, event_id):
        """Update an event given its id"""
        event = DAO.update(event_id, self.api.payload)
        record_activity('update_event', event_id=event_id)
        return event


@api.route('/<int:event_id>/event')
@api.param('event_id')
@api.response(404, 'Event not found')
class EventWebapp(Resource, SingleEventResource):
    @api.doc('get_event_for_webapp')
    @api.header(*ETAG_HEADER_DEFN)
    @fake_marshal_with(EVENT_COMPLETE)  # Fake marshal decorator to add response model to swagger doc
    def get(self, event_id):
        """Fetch an event given its id.
        Alternate endpoint for fetching an event.
        """
        includes = parse_args(self.event_parser).get('include', '').split(',')
        return marshal(DAO.get(event_id), get_extended_event_model(includes))


@api.route('')
class EventList(Resource, EventResource):
    @api.doc('list_events', params=EVENT_PARAMS)
    @api.header(*ETAG_HEADER_DEFN)
    @fake_marshal_list_with(EVENT_COMPLETE)
    def get(self):
        """List all events"""
        parsed_args = parse_args(self.event_parser)
        includes = parsed_args.get('include', '').split(',')
        erase_from_dict(parsed_args, 'include')
        return marshal(DAO.list(**parsed_args), get_extended_event_model(includes))

    @requires_auth
    @api.doc('create_event', responses=POST_RESPONSES)
    @api.marshal_with(EVENT)
    @api.expect(EVENT_POST)
    def post(self):
        """Create an event"""
        item = DAO.create(self.api.payload, self.api.url_for(self))
        record_activity('create_event', event_id=item[0].id)
        return item


@api.route('/page')
class EventListPaginated(Resource, PaginatedResourceBase, EventResource):
    @api.doc('list_events_paginated', params=PAGE_PARAMS)
    @api.doc(params=EVENT_PARAMS)
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_with(EVENT_PAGINATED)
    def get(self):
        """List events in a paginated manner"""
        args = self.parser.parse_args()
        return DAO.paginated_list(args=args, **parse_args(self.event_parser))


@api.route('/<int:event_id>/links')
@api.param('event_id')
class SocialLinkList(Resource):
    @api.doc('list_social_links')
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_list_with(SOCIAL_LINK)
    def get(self, event_id):
        """List all social links"""
        return LinkDAO.list(event_id)

    @requires_auth
    @can_access
    @api.doc('create_social_link', responses=POST_RESPONSES)
    @api.marshal_with(SOCIAL_LINK)
    @api.expect(SOCIAL_LINK_POST)
    def post(self, event_id):
        """Create a social link"""
        return LinkDAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )


@api.route('/<int:event_id>/links/<int:link_id>')
class SocialLink(Resource):
    @requires_auth
    @can_access
    @api.doc('delete_social_link')
    @api.marshal_with(SOCIAL_LINK)
    def delete(self, event_id, link_id):
        """Delete a social link given its id"""
        return LinkDAO.delete(event_id, link_id)

    @requires_auth
    @can_access
    @api.doc('update_social_link', responses=PUT_RESPONSES)
    @api.marshal_with(SOCIAL_LINK)
    @api.expect(SOCIAL_LINK_POST)
    def put(self, event_id, link_id):
        """Update a social link given its id"""
        return LinkDAO.update(event_id, link_id, self.api.payload)

    @api.hide
    @api.header(*ETAG_HEADER_DEFN)
    @api.marshal_with(SOCIAL_LINK)
    def get(self, event_id, link_id):
        """Fetch a social link given its id"""
        return LinkDAO.get(event_id, link_id)

from datetime import datetime

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from pytz import timezone
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound, BadRequest
from marshmallow import validates_schema
from flask import request

from app.api.bootstrap import api
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event
from app.models.sponsor import Sponsor
from app.models.track import Track
from app.models.session import Session
from app.models.ticket import Ticket
from app.models.session_type import SessionType
from app.models.discount_code import DiscountCode
from app.models.event_invoice import EventInvoice
from app.models.speakers_call import SpeakersCall
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.models.ticket import TicketTag
from app.models.user import User, ATTENDEE, ORGANIZER
from app.models.users_events_role import UsersEventsRoles
from app.models.role import Role
from app.api.helpers.db import save_to_db, safe_query
from app.api.helpers.exceptions import UnprocessableEntity


class EventSchema(Schema):

    class Meta:
        type_ = 'event'
        self_view = 'v1.event_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.event_list'
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            event = Event.query.filter_by(id=original_data['data']['id']).one()

            if 'starts_at' not in data:
                data['starts_at'] = event.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = event.ends_at

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'},
                                      "ends-at should be after starts-at")

    @validates_schema
    def validate_timezone(self, data):
        if 'timezone' in data:
            offset = timezone(data['timezone']).utcoffset(
                datetime.strptime('2014-12-01', '%Y-%m-%d')).seconds
            if 'starts_at' in data:
                starts_at = data['starts_at'].utcoffset().seconds
                if offset != starts_at:
                    raise UnprocessableEntity({'pointer': '/data/attributes/timezone'},
                                              "timezone: {} does not match with the starts-at "
                                              "offset {:02}:{:02}".
                                              format(data['timezone'], starts_at // 3600, starts_at % 3600 // 60))
            if 'ends_at' in data:
                ends_at = data['ends_at'].utcoffset().seconds
                if offset != ends_at:
                    raise UnprocessableEntity({'pointer': '/data/attributes/timezone'},
                                              "timezone: {} does not match with the ends-at "
                                              "offset {:02}:{:02}".
                                              format(data['timezone'], ends_at // 3600, ends_at % 3600 // 60))

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    external_event_url = fields.Url(allow_none=True)
    starts_at = fields.DateTime(required=True, timezone=True)
    ends_at = fields.DateTime(required=True, timezone=True)
    timezone = fields.Str(required=True)
    latitude = fields.Float(validate=lambda n: -90 <= n <= 90, allow_none=True)
    longitude = fields.Float(validate=lambda n: -180 <= n <= 180, allow_none=True)
    logo_url = fields.Url(allow_none=True)
    location_name = fields.Str(allow_none=True)
    searchable_location_name = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    original_image_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(dump_only=True)
    large_image_url = fields.Url(dump_only=True)
    icon_image_url = fields.Url(dump_only=True)
    organizer_name = fields.Str(allow_none=True)
    is_map_shown = fields.Bool(default=False)
    has_organizer_info = fields.Bool(default=False)
    organizer_description = fields.Str(allow_none=True)
    is_sessions_speakers_enabled = fields.Bool(default=False)
    privacy = fields.Str(default="public")
    state = fields.Str(default="Draft")
    ticket_url = fields.Url(allow_none=True)
    code_of_conduct = fields.Str(allow_none=True)
    schedule_published_on = fields.DateTime(allow_none=True)
    is_ticketing_enabled = fields.Bool(default=True)
    deleted_at = fields.DateTime(allow_none=True)
    payment_country = fields.Str(allow_none=True)
    payment_currency = fields.Str(allow_none=True)
    paypal_email = fields.Str(allow_none=True)
    is_tax_enabled = fields.Bool(default=False)
    can_pay_by_paypal = fields.Bool(default=False)
    can_pay_by_stripe = fields.Bool(default=False)
    can_pay_by_cheque = fields.Bool(default=False)
    can_pay_by_bank = fields.Bool(default=False)
    can_pay_onsite = fields.Bool(default=False)
    cheque_details = fields.Str(allow_none=True)
    bank_details = fields.Str(allow_none=True)
    onsite_details = fields.Str(allow_none=True)
    is_sponsors_enabled = fields.Bool(default=False)
    created_at = fields.DateTime(dump_only=True, timezone=True)
    pentabarf_url = fields.Url(dump_only=True)
    ical_url = fields.Url(dump_only=True)
    xcal_url = fields.Url(dump_only=True)
    tickets = Relationship(attribute='tickets',
                           self_view='v1.event_ticket',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'event_id': '<id>'},
                           schema='TicketSchema',
                           many=True,
                           type_='ticket')
    ticket_tags = Relationship(attribute='ticket_tags',
                               self_view='v1.event_ticket_tag',
                               self_view_kwargs={'id': '<id>'},
                               related_view='v1.ticket_tag_list',
                               related_view_kwargs={'event_id': '<id>'},
                               schema='TicketTagSchema',
                               many=True,
                               type_='ticket-tag')
    microlocations = Relationship(attribute='microlocation',
                                  self_view='v1.event_microlocation',
                                  self_view_kwargs={'id': '<id>'},
                                  related_view='v1.microlocation_list',
                                  related_view_kwargs={'event_id': '<id>'},
                                  schema='MicrolocationSchema',
                                  many=True,
                                  type_='microlocation')
    social_links = Relationship(attribute='social_link',
                                self_view='v1.event_social_link',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.social_link_list',
                                related_view_kwargs={'event_id': '<id>'},
                                schema='SocialLinkSchema',
                                many=True,
                                type_='social-link')
    tracks = Relationship(attribute='track',
                          self_view='v1.event_tracks',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.track_list',
                          related_view_kwargs={'event_id': '<id>'},
                          schema='TrackSchema',
                          many=True,
                          type_='track')
    sponsors = Relationship(attribute='sponsor',
                            self_view='v1.event_sponsor',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.sponsor_list',
                            related_view_kwargs={'event_id': '<id>'},
                            schema='SponsorSchema',
                            many=True,
                            type_='sponsor')
    speakers_call = Relationship(attribute='speakers_call',
                                 self_view='v1.event_speakers_call',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.speakers_call_detail',
                                 related_view_kwargs={'event_id': '<id>'},
                                 schema='SpeakersCallSchema',
                                 type_='speakers-call')
    session_types = Relationship(attribute='session_type',
                                 self_view='v1.event_session_types',
                                 self_view_kwargs={'id': '<id>'},
                                 related_view='v1.session_type_list',
                                 related_view_kwargs={'event_id': '<id>'},
                                 schema='SessionTypeSchema',
                                 many=True,
                                 type_='session-type')
    event_copyright = Relationship(attribute='copyright',
                                   self_view='v1.event_copyright',
                                   self_view_kwargs={'id': '<id>'},
                                   related_view='v1.event_copyright_detail',
                                   related_view_kwargs={'event_id': '<id>'},
                                   schema='EventCopyrightSchema',
                                   type_='event-copyright')
    tax = Relationship(self_view='v1.event_tax',
                       self_view_kwargs={'id': '<id>'},
                       related_view='v1.tax_detail',
                       related_view_kwargs={'event_id': '<id>'},
                       schema='TaxSchema',
                       type_='tax')
    event_invoices = Relationship(attribute='invoices',
                                  self_view='v1.event_event_invoice',
                                  self_view_kwargs={'id': '<id>'},
                                  related_view='v1.event_invoice_list',
                                  related_view_kwargs={'event_id': '<id>'},
                                  schema='EventInvoiceSchema',
                                  many=True,
                                  type_='event-invoice')
    discount_codes = Relationship(attribute='discount_code',
                                  self_view='v1.event_discount_code',
                                  self_view_kwargs={'id': '<id>'},
                                  related_view='v1.discount_code_list',
                                  related_view_kwargs={'event_id': '<id>'},
                                  schema='DiscountCodeSchema',
                                  many=True,
                                  type_='discount-code')
    sessions = Relationship(attribute='session',
                            self_view='v1.event_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'event_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')
    event_type = Relationship(attribute='event_type',
                              self_view='v1.event_event_type',
                              self_view_kwargs={'id': '<id>'},
                              related_view='v1.event_type_detail',
                              related_view_kwargs={'event_id': '<id>'},
                              schema='EventTypeSchema',
                              type_='event-type')
    event_topic = Relationship(attribute='event_topic',
                               self_view='v1.event_event_topic',
                               self_view_kwargs={'id': '<id>'},
                               related_view='v1.event_topic_detail',
                               related_view_kwargs={'event_id': '<id>'},
                               schema='EventTopicSchema',
                               type_='event-topic')
    event_sub_topic = Relationship(attribute='event_sub_topic',
                                   self_view='v1.event_event_sub_topic',
                                   self_view_kwargs={'id': '<id>'},
                                   related_view='v1.event_sub_topic_detail',
                                   related_view_kwargs={'event_id': '<id>'},
                                   schema='EventSubTopicSchema',
                                   type_='event-sub-topic')
    role_invites = Relationship(attribute='role_invites',
                                self_view='v1.event_role_invite',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.role_invite_list',
                                related_view_kwargs={'event_id': '<id>'},
                                schema='RoleInviteSchema',
                                type_='role-invite')


class EventList(ResourceList):

    def query(self, view_kwargs):
        query_ = self.session.query(Event)
        if view_kwargs.get('user_id') and 'GET' in request.method:
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(Event.roles).filter_by(user_id=user.id).join(UsersEventsRoles.role).\
                filter(Role.name != ATTENDEE)

        elif view_kwargs.get('event_type_id') and 'GET' in request.method:
            event = safe_query(self, Event, 'event_type_id', view_kwargs['event_type_id'], 'event_type_id')
            query_ = self.session.query(Event).filter_by(event_type_id=event.event_type_id)

        elif view_kwargs.get('event_topic_id') and 'GET' in request.method:
            event = safe_query(self, Event, 'event_topic_id', view_kwargs['event_topic_id'], 'event_topic_id')
            query_ = self.session.query(Event).filter_by(event_topic_id=event.event_topic_id)

        elif view_kwargs.get('event_sub_topic_id') and 'GET' in request.method:
            event = safe_query(self, Event, 'event_sub_topic_id', view_kwargs['event_sub_topic_id'],
                               'event_sub_topic_id')
            query_ = self.session.query(Event).filter_by(event_sub_topic_id=event.event_sub_topic_id)

        elif view_kwargs.get('discount_code_id') and 'GET' in request.method:
            event = safe_query(self, Event, 'discount_code_id', view_kwargs['discount_code_id'],
                               'discount_code_id')
            query_ = self.session.query(Event).filter_by(discount_code_id=event.discount_code_id)

        return query_

    def after_create_object(self, event, data, view_kwargs):
        role = Role.query.filter_by(name=ORGANIZER).first()
        user = User.query.filter_by(id=view_kwargs['user_id']).first()
        uer = UsersEventsRoles(user, event, role)
        save_to_db(uer, 'Event Saved')

    # This permission decorator ensures, you are logged in to create an event
    # and have filter ?withRole to get events associated with logged in user
    decorators = (api.has_permission('accessible_role_based_events'),)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'after_create_object': after_create_object,
                              'query': query
                              }}


class EventDetail(ResourceDetail):

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            view_kwargs['id'] = event.id

        if view_kwargs.get('sponsor_id') is not None:
            sponsor = safe_query(self, Sponsor, 'id', view_kwargs['sponsor_id'], 'sponsor_id')
            if sponsor.event_id is not None:
                view_kwargs['id'] = sponsor.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('track_id') is not None:
            track = safe_query(self, Track, 'id', view_kwargs['track_id'], 'track_id')
            if track.event_id is not None:
                view_kwargs['id'] = track.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('session_type_id') is not None:
            session_type = safe_query(self, SessionType, 'id', view_kwargs['session_type_id'], 'session_type_id')
            if session_type.event_id is not None:
                view_kwargs['id'] = session_type.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_id') is not None:
            event_invoice = safe_query(self, EventInvoice, 'id', view_kwargs['event_invoice_id'], 'event_invoice_id')
            if event_invoice.event_id is not None:
                view_kwargs['id'] = event_invoice.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('discount_code_id') is not None:
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            if discount_code.event_id is not None:
                view_kwargs['id'] = discount_code.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('session_id') is not None:
            sessions = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            if sessions.event_id is not None:
                view_kwargs['id'] = sessions.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('user_id') is not None:
            try:
                discount_code = self.session.query(DiscountCode).filter_by(
                    id=view_kwargs['discount_code_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'discount_code_id'},
                                     "DiscountCode: {} not found".format(view_kwargs['discount_code_id']))
            else:
                if discount_code.event_id is not None:
                    view_kwargs['id'] = discount_code.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('speakers_call_id') is not None:
            speakers_call = safe_query(self, SpeakersCall, 'id', view_kwargs['speakers_call_id'], 'speakers_call_id')
            if speakers_call.event_id is not None:
                view_kwargs['id'] = speakers_call.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('ticket_id') is not None:
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if ticket.event_id is not None:
                view_kwargs['id'] = ticket.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('ticket_tag_id') is not None:
            ticket_tag = safe_query(self, TicketTag, 'id', view_kwargs['ticket_tag_id'], 'ticket_tag_id')
            if ticket_tag.event_id is not None:
                view_kwargs['id'] = ticket_tag.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('role_invite_id') is not None:
            role_invite = safe_query(self, RoleInvite, 'id', view_kwargs['role_invite_id'], 'role_invite_id')
            if role_invite.event_id is not None:
                view_kwargs['id'] = role_invite.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
            users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
            'users_events_role_id')
            if users_events_role.event_id is not None:
                view_kwargs['id'] = users_events_role.event_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_organizer', methods="PATCH,DELETE", fetch="id", fetch_as="event_id",
                                     check=lambda a: a.get('id') is not None), )
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventRelationship(ResourceRelationship):

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            view_kwargs['id'] = event.id

    decorators = (jwt_required,)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'before_get_object': before_get_object}
                  }

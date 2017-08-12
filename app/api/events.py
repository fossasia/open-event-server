import pytz

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from pytz import timezone
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validates_schema
from flask import request, current_app
import marshmallow.validate as validate
from flask_jwt import current_identity, _jwt_required
from sqlalchemy import or_

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event
from app.models.sponsor import Sponsor
from app.models.track import Track
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket import Ticket
from app.models.session_type import SessionType
from app.models.discount_code import DiscountCode
from app.models.event_invoice import EventInvoice
from app.models.speakers_call import SpeakersCall
from app.models.role_invite import RoleInvite
from app.models.custom_form import CustomForms
from app.models.ticket import TicketTag
from app.models.access_code import AccessCode
from app.models.user import User, ATTENDEE, ORGANIZER, COORGANIZER
from app.models.users_events_role import UsersEventsRoles
from app.models.role import Role
from app.models.ticket_holder import TicketHolder
from app.api.helpers.db import save_to_db, safe_query
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.files import create_save_image_sizes
from app.models.microlocation import Microlocation
from app.models.email_notification import EmailNotification
from app.models.social_link import SocialLink
from app.models.tax import Tax
from app.models.event_copyright import EventCopyright


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

        if 'starts_at' not in data or 'ends_at' not in data:
            raise UnprocessableEntity({'pointer': '/data/attributes/date'},
                                      "enter required fields starts-at/ends-at")

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'},
                                      "ends-at should be after starts-at")

    @validates_schema(pass_original=True)
    def validate_timezone(self, data, original_data):
        if 'id' in original_data['data']:
            event = Event.query.filter_by(id=original_data['data']['id']).one()

            if 'timezone' not in data:
                data['timezone'] = event.timezone
        try:
            timezone(data['timezone'])
        except pytz.exceptions.UnknownTimeZoneError:
            raise UnprocessableEntity({'pointer': '/data/attributes/timezone'},
                                      "Unknown timezone: '{}'".
                                      format(data['timezone']))

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
    state = fields.Str(validate=validate.OneOf(choices=["published", "draft"]), allow_none=True, default='draft')
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
                                  type_='discount-code')
    sessions = Relationship(attribute='session',
                            self_view='v1.event_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'event_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')
    speakers = Relationship(attribute='speaker',
                            self_view='v1.event_speaker',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.speaker_list',
                            related_view_kwargs={'event_id': '<id>'},
                            schema='SpeakerSchema',
                            many=True,
                            type_='speaker')
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
    access_codes = Relationship(attribute='access_codes',
                                self_view='v1.event_access_codes',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.access_code_list',
                                related_view_kwargs={'event_id': '<id>'},
                                schema='AccessCodeSchema',
                                many=True,
                                type_='access-code')
    attendees = Relationship(attribute='attendees',
                             self_view='v1.event_attendees',
                             self_view_kwargs={'id': '<id>'},
                             related_view='v1.attendee_list',
                             related_view_kwargs={'event_id': '<id>'},
                             schema='AttendeeSchema',
                             many=True,
                             type_='attendee')
    custom_forms = Relationship(attribute='custom_form',
                                self_view='v1.event_custom_forms',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.custom_form_list',
                                related_view_kwargs={'event_id': '<id>'},
                                schema='CustomFormSchema',
                                many=True,
                                type_='custom-form')
    organizers = Relationship(attribute='organizers',
                              self_view='v1.event_organizers',
                              self_view_kwargs={'id': '<id>'},
                              related_view='v1.user_list',
                              schema='UserSchema',
                              type_='user',
                              many=True)
    coorganizers = Relationship(attribute='coorganizers',
                                self_view='v1.event_coorganizers',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.user_list',
                                schema='UserSchema',
                                type_='user',
                                many=True)
    track_organizers = Relationship(attribute='track_organizers',
                                    self_view='v1.event_track_organizers',
                                    self_view_kwargs={'id': '<id>'},
                                    related_view='v1.user_list',
                                    schema='UserSchema',
                                    type_='user',
                                    many=True)
    moderators = Relationship(attribute='moderators',
                              self_view='v1.event_moderators',
                              self_view_kwargs={'id': '<id>'},
                              related_view='v1.user_list',
                              schema='UserSchema',
                              type_='user',
                              many=True)
    registrars = Relationship(attribute='registrars',
                              self_view='v1.event_registrars',
                              self_view_kwargs={'id': '<id>'},
                              related_view='v1.user_list',
                              schema='UserSchema',
                              type_='user',
                              many=True)


class EventList(ResourceList):
    def query(self, view_kwargs):
        query_ = self.session.query(Event).filter_by(state='published')
        if 'Authorization' in request.headers:
            _jwt_required(current_app.config['JWT_DEFAULT_REALM'])
            query2 = self.session.query(Event)
            query2 = query2.join(Event.roles).filter_by(user_id=current_identity.id).join(UsersEventsRoles.role). \
                filter(or_(Role.name == COORGANIZER, Role.name == ORGANIZER))
            query_ = query_.union(query2)

        if view_kwargs.get('user_id') and 'GET' in request.method:
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(Event.roles).filter_by(user_id=user.id).join(UsersEventsRoles.role). \
                filter(Role.name != ATTENDEE)

        if view_kwargs.get('event_type_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_type_id') == view_kwargs['event_type_id'])

        if view_kwargs.get('event_topic_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_topic_id') == view_kwargs['event_topic_id'])

        if view_kwargs.get('event_sub_topic_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_sub_topic_id') == view_kwargs['event_sub_topic_id'])

        if view_kwargs.get('discount_code_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'discount_code_id') == view_kwargs['discount_code_id'])

        return query_

    def after_create_object(self, event, data, view_kwargs):
        role = Role.query.filter_by(name=ORGANIZER).first()
        user = User.query.filter_by(id=view_kwargs['user_id']).first()
        uer = UsersEventsRoles(user, event, role)
        save_to_db(uer, 'Event Saved')
        if data.get('original_image_url'):
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'event', event.id)
            self.session.query(Event).filter_by(id=event.id).update(uploaded_images)

    # This permission decorator ensures, you are logged in to create an event
    # and have filter ?withRole to get events associated with logged in user
    decorators = (api.has_permission('create_event'),)
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

        if view_kwargs.get('copyright_id') is not None:
            copyright = safe_query(self, EventCopyright, 'id', view_kwargs['copyright_id'], 'copyright_id')
            if copyright.event_id is not None:
                view_kwargs['id'] = copyright.event_id
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

        if view_kwargs.get('social_link_id') is not None:
            social_link = safe_query(self, SocialLink, 'id', view_kwargs['social_link_id'], 'social_link_id')
            if social_link.event_id is not None:
                view_kwargs['id'] = social_link.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('tax_id') is not None:
            tax = safe_query(self, Tax, 'id', view_kwargs['tax_id'], 'tax_id')
            if tax.event_id is not None:
                view_kwargs['id'] = tax.event_id
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

        if view_kwargs.get('access_code_id') is not None:
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            if access_code.event_id is not None:
                view_kwargs['id'] = access_code.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('speaker_id'):
            try:
                speaker = self.session.query(Speaker).filter_by(id=view_kwargs['speaker_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'speaker_id'},
                                     "Speaker: {} not found".format(view_kwargs['speaker_id']))
            else:
                if speaker.event_id:
                    view_kwargs['id'] = speaker.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('email_notification_id'):
            try:
                email_notification = self.session.query(EmailNotification).filter_by(
                                     id=view_kwargs['email_notification_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'email_notification_id'},
                                     "Email Notification: {} not found".format(view_kwargs['email_notification_id']))
            else:
                if email_notification.event_id:
                    view_kwargs['id'] = email_notification.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('microlocation_id'):
            try:
                microlocation = self.session.query(Microlocation).filter_by(id=view_kwargs['microlocation_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'microlocation_id'},
                                     "Microlocation: {} not found".format(view_kwargs['microlocation_id']))
            else:
                if microlocation.event_id:
                    view_kwargs['id'] = microlocation.event_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('attendee_id'):
            attendee = safe_query(self, TicketHolder, 'id', view_kwargs['attendee_id'], 'attendee_id')
            if attendee.event_id is not None:
                view_kwargs['id'] = attendee.event_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('custom_form_id') is not None:
            custom_form = safe_query(self, CustomForms, 'id', view_kwargs['custom_form_id'], 'custom_form_id')
            if custom_form.event_id is not None:
                view_kwargs['id'] = custom_form.event_id
            else:
                view_kwargs['id'] = None

    def before_update_object(self, event, data, view_kwargs):

        if data.get('original_image_url') and data['original_image_url'] != event.original_image_url:
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'event', event.id)
            data['original_image_url'] = uploaded_images['original_image_url']
            data['large_image_url'] = uploaded_images['large_image_url']
            data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
            data['icon_image_url'] = uploaded_images['icon_image_url']
        else:
            if data.get('large_image_url'):
                del data['large_image_url']
            if data.get('thumbnail_image_url'):
                del data['thumbnail_image_url']
            if data.get('icon_image_url'):
                del data['icon_image_url']

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="id", fetch_as="event_id",
                                     model=Event), )
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object
                  }}


class EventRelationship(ResourceRelationship):

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            view_kwargs['id'] = event.id

    decorators = (api.has_permission('is_coorganizer', fetch="id", fetch_as="event_id",
                                     model=Event),)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'before_get_object': before_get_object}
                  }

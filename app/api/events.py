from flask import request, current_app
from flask_jwt import current_identity, _jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import or_
from sqlalchemy.orm.exc import NoResultFound
import pytz
from datetime import datetime
from app.api.bootstrap import api
from app.api.data_layers.EventCopyLayer import EventCopyLayer
from app.api.helpers.db import save_to_db, safe_query
from app.api.helpers.events import create_custom_forms_for_attendees
from app.api.helpers.exceptions import ForbiddenException, ConflictException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import dasherize
from app.api.schema.events import EventSchemaPublic, EventSchema
from app.api.helpers.export_helpers import create_export_job
# models
from app.models import db
from app.models.access_code import AccessCode
from app.models.module import Module
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
from app.models.email_notification import EmailNotification
from app.models.event import Event
from app.models.event_copyright import EventCopyright
from app.models.event_invoice import EventInvoice
from app.models.faq import Faq
from app.models.faq_type import FaqType
from app.models.feedback import Feedback
from app.models.microlocation import Microlocation
from app.models.order import Order
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.social_link import SocialLink
from app.models.speaker import Speaker
from app.models.speakers_call import SpeakersCall
from app.models.sponsor import Sponsor
from app.models.tax import Tax
from app.models.ticket import Ticket
from app.models.ticket import TicketTag
from app.models.ticket_holder import TicketHolder
from app.models.track import Track
from app.models.user_favourite_event import UserFavouriteEvent
from app.models.user import User, ATTENDEE, ORGANIZER, COORGANIZER
from app.models.users_events_role import UsersEventsRoles
from app.models.stripe_authorization import StripeAuthorization


def validate_event(user, modules, data):
    if not user.can_create_event():
        raise ForbiddenException({'source': ''},
                                 "Please verify your Email")
    elif data.get('is_ticketing_enabled', True) and not modules.ticket_include:
            raise ForbiddenException({'source': '/data/attributes/is-ticketing-enabled'},
                                     "Ticketing is not enabled in the system")
    if data.get('can_pay_by_paypal', False) or data.get('can_pay_by_cheque', False) or \
        data.get('can_pay_by_bank', False) or data.get('can_pay_by_stripe', False):
        if not modules.payment_include:
            raise ForbiddenException({'source': ''},
                                     "Payment is not enabled in the system")
    if data.get('is_donation_enabled', False) and not modules.donation_include:
        raise ForbiddenException({'source': '/data/attributes/is-donation-enabled'},
                                 "Donation is not enabled in the system")

    if data.get('state', None) == 'published' and not user.can_publish_event():
        raise ForbiddenException({'source': ''},
                                 "Only verified accounts can publish events")

    if not data.get('is_event_online') and data.get('state', None) == 'published' \
        and not data.get('location_name', None):
        raise ConflictException({'pointer': '/data/attributes/location-name'},
                                "Location is required to publish the event")

    if data.get('location_name', None) and data.get('is_event_online'):
        raise ConflictException({'pointer': '/data/attributes/location-name'},
                                "Online Event does not have any locaton")

    if data.get('searchable_location_name') and data.get('is_event_online'):
        raise ConflictException({'pointer': '/data/attributes/searchable-location-name'},
                                "Online Event does not have any locaton")


class EventList(ResourceList):
    def before_get(self, args, kwargs):
        """
        method for assigning schema based on admin access
        :param args:
        :param kwargs:
        :return:
        """
        if 'Authorization' in request.headers and (has_access('is_admin') or kwargs.get('user_id')):
            self.schema = EventSchema
        else:
            self.schema = EventSchemaPublic

    def query(self, view_kwargs):
        """
        query method for EventList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Event).filter_by(state='published')
        if 'Authorization' in request.headers:
            _jwt_required(current_app.config['JWT_DEFAULT_REALM'])
            query2 = self.session.query(Event)
            query2 = query2.join(Event.roles).filter_by(user_id=current_identity.id).join(UsersEventsRoles.role). \
                filter(or_(Role.name == COORGANIZER, Role.name == ORGANIZER))
            query_ = query_.union(query2)

        if view_kwargs.get('user_id') and 'GET' in request.method:
            if not has_access('is_user_itself', user_id=int(view_kwargs['user_id'])):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            user = safe_query(db, User, 'id', view_kwargs['user_id'], 'user_id')
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
            event_id = get_id(view_kwargs)['id']
            if not has_access('is_coorganizer', event_id=event_id):
                raise ForbiddenException({'source': ''}, 'Coorganizer access is required')
            query_ = self.session.query(Event).filter(
                getattr(Event, 'discount_code_id') == view_kwargs['discount_code_id'])

        return query_

    def before_post(self, args, kwargs, data=None):
        """
        before post method to verify if the event location is provided before publishing the event
        and checks that the user is verified
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        user = User.query.filter_by(id=kwargs['user_id']).first()
        modules = Module.query.first()
        validate_event(user, modules, data)

    def after_create_object(self, event, data, view_kwargs):
        """
        after create method to save roles for users and add the user as an accepted role(organizer)
        :param event:
        :param data:
        :param view_kwargs:
        :return:
        """
        role = Role.query.filter_by(name=ORGANIZER).first()
        user = User.query.filter_by(id=view_kwargs['user_id']).first()
        uer = UsersEventsRoles(user, event, role)
        save_to_db(uer, 'Event Saved')
        role_invite = RoleInvite(user.email, role.title_name, event.id, role.id, datetime.now(pytz.utc),
                                 status='accepted')
        save_to_db(role_invite, 'Organiser Role Invite Added')

        # create custom forms for compulsory fields of attendee form.
        create_custom_forms_for_attendees(event)

        if event.state == 'published' and event.schedule_published_on:
            start_export_tasks(event)

        if data.get('original_image_url'):
            start_image_resizing_tasks(event, data['original_image_url'])

    # This permission decorator ensures, you are logged in to create an event
    # and have filter ?withRole to get events associated with logged in user
    decorators = (api.has_permission('create_event', ),)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'after_create_object': after_create_object,
                              'query': query
                              }}


def get_id(view_kwargs):
    """
    method to get the resource id for fetching details
    :param view_kwargs:
    :return:
    """
    if view_kwargs.get('identifier'):
        event = safe_query(db, Event, 'identifier', view_kwargs['identifier'], 'identifier')
        view_kwargs['id'] = event.id

    if view_kwargs.get('sponsor_id') is not None:
        sponsor = safe_query(db, Sponsor, 'id', view_kwargs['sponsor_id'], 'sponsor_id')
        if sponsor.event_id is not None:
            view_kwargs['id'] = sponsor.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('user_favourite_event_id') is not None:
        user_favourite_event = safe_query(db, UserFavouriteEvent, 'id',
                                          view_kwargs['user_favourite_event_id'], 'user_favourite_event_id')
        if user_favourite_event.event_id is not None:
            view_kwargs['id'] = user_favourite_event.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('copyright_id') is not None:
        copyright = safe_query(db, EventCopyright, 'id', view_kwargs['copyright_id'], 'copyright_id')
        if copyright.event_id is not None:
            view_kwargs['id'] = copyright.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('track_id') is not None:
        track = safe_query(db, Track, 'id', view_kwargs['track_id'], 'track_id')
        if track.event_id is not None:
            view_kwargs['id'] = track.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('session_type_id') is not None:
        session_type = safe_query(db, SessionType, 'id', view_kwargs['session_type_id'], 'session_type_id')
        if session_type.event_id is not None:
            view_kwargs['id'] = session_type.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('faq_type_id') is not None:
        faq_type = safe_query(db, FaqType, 'id', view_kwargs['faq_type_id'], 'faq_type_id')
        if faq_type.event_id is not None:
            view_kwargs['id'] = faq_type.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('event_invoice_id') is not None:
        event_invoice = safe_query(db, EventInvoice, 'id', view_kwargs['event_invoice_id'], 'event_invoice_id')
        if event_invoice.event_id is not None:
            view_kwargs['id'] = event_invoice.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('discount_code_id') is not None:
        discount_code = safe_query(db, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
        if discount_code.event_id is not None:
            view_kwargs['id'] = discount_code.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('session_id') is not None:
        sessions = safe_query(db, Session, 'id', view_kwargs['session_id'], 'session_id')
        if sessions.event_id is not None:
            view_kwargs['id'] = sessions.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('social_link_id') is not None:
        social_link = safe_query(db, SocialLink, 'id', view_kwargs['social_link_id'], 'social_link_id')
        if social_link.event_id is not None:
            view_kwargs['id'] = social_link.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('tax_id') is not None:
        tax = safe_query(db, Tax, 'id', view_kwargs['tax_id'], 'tax_id')
        if tax.event_id is not None:
            view_kwargs['id'] = tax.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('stripe_authorization_id') is not None:
        stripe_authorization = safe_query(db, StripeAuthorization, 'id', view_kwargs['stripe_authorization_id'],
                                          'stripe_authorization_id')
        if stripe_authorization.event_id is not None:
            view_kwargs['id'] = stripe_authorization.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('user_id') is not None:
        try:
            discount_code = db.session.query(DiscountCode).filter_by(
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
        speakers_call = safe_query(db, SpeakersCall, 'id', view_kwargs['speakers_call_id'], 'speakers_call_id')
        if speakers_call.event_id is not None:
            view_kwargs['id'] = speakers_call.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('ticket_id') is not None:
        ticket = safe_query(db, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
        if ticket.event_id is not None:
            view_kwargs['id'] = ticket.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('ticket_tag_id') is not None:
        ticket_tag = safe_query(db, TicketTag, 'id', view_kwargs['ticket_tag_id'], 'ticket_tag_id')
        if ticket_tag.event_id is not None:
            view_kwargs['id'] = ticket_tag.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('role_invite_id') is not None:
        role_invite = safe_query(db, RoleInvite, 'id', view_kwargs['role_invite_id'], 'role_invite_id')
        if role_invite.event_id is not None:
            view_kwargs['id'] = role_invite.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('users_events_role_id') is not None:
        users_events_role = safe_query(db, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
                                       'users_events_role_id')
        if users_events_role.event_id is not None:
            view_kwargs['id'] = users_events_role.event_id

    if view_kwargs.get('access_code_id') is not None:
        access_code = safe_query(db, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
        if access_code.event_id is not None:
            view_kwargs['id'] = access_code.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('speaker_id'):
        try:
            speaker = db.session.query(Speaker).filter_by(id=view_kwargs['speaker_id']).one()
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
            email_notification = db.session.query(EmailNotification).filter_by(
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
            microlocation = db.session.query(Microlocation).filter_by(id=view_kwargs['microlocation_id']).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': 'microlocation_id'},
                                 "Microlocation: {} not found".format(view_kwargs['microlocation_id']))
        else:
            if microlocation.event_id:
                view_kwargs['id'] = microlocation.event_id
            else:
                view_kwargs['id'] = None

    if view_kwargs.get('attendee_id'):
        attendee = safe_query(db, TicketHolder, 'id', view_kwargs['attendee_id'], 'attendee_id')
        if attendee.event_id is not None:
            view_kwargs['id'] = attendee.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('custom_form_id') is not None:
        custom_form = safe_query(db, CustomForms, 'id', view_kwargs['custom_form_id'], 'custom_form_id')
        if custom_form.event_id is not None:
            view_kwargs['id'] = custom_form.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('faq_id') is not None:
        faq = safe_query(db, Faq, 'id', view_kwargs['faq_id'], 'faq_id')
        if faq.event_id is not None:
            view_kwargs['id'] = faq.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('order_identifier') is not None:
        order = safe_query(db, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
        if order.event_id is not None:
            view_kwargs['id'] = order.event_id
        else:
            view_kwargs['id'] = None

    if view_kwargs.get('feedback_id') is not None:
        feedback = safe_query(db, Feedback, 'id', view_kwargs['feedback_id'], 'feedback_id')
        if feedback.event_id is not None:
            view_kwargs['id'] = feedback.event_id
        else:
            view_kwargs['id'] = None

    return view_kwargs


class EventDetail(ResourceDetail):
    """
    EventDetail class for EventSchema
    """

    def before_get(self, args, kwargs):
        """
        method for assigning schema based on access
        :param args:
        :param kwargs:
        :return:
        """
        kwargs = get_id(kwargs)
        if 'Authorization' in request.headers and has_access('is_coorganizer', event_id=kwargs['id']):
            self.schema = EventSchema
        else:
            self.schema = EventSchemaPublic

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        get_id(view_kwargs)

        if view_kwargs.get('order_identifier') is not None:
            order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
            if order.event_id is not None:
                view_kwargs['id'] = order.event_id
            else:
                view_kwargs['id'] = None

    def before_patch(self, args, kwargs, data=None):
        """
        before patch method to verify if the event location is provided before publishing the event and checks that
        the user is verified
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        user = User.query.filter_by(id=current_identity.id).one()
        modules = Module.query.first()
        validate_event(user, modules, data)

    def before_update_object(self, event, data, view_kwargs):
        """
        method to save image urls before updating event object
        :param event:
        :param data:
        :param view_kwargs:
        :return:
        """

        if has_access('is_admin') and data.get('deleted_at') != event.deleted_at:
            event.deleted_at = data.get('deleted_at')

        if 'is_event_online' not in data and event.is_event_online \
                or 'is_event_online' in data and not data['is_event_online']:
            if data.get('state', None) == 'published' and not data.get('location_name', None):
                raise ConflictException({'pointer': '/data/attributes/location-name'},
                                        "Location is required to publish the event")
        if data.get('original_image_url') and data['original_image_url'] != event.original_image_url:
            start_image_resizing_tasks(event, data['original_image_url'])

    def after_update_object(self, event, data, view_kwargs):
        if event.state == 'published' and event.schedule_published_on:
            start_export_tasks(event)
        else:
            clear_export_urls(event)

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="id", fetch_as="event_id",
                                     model=Event),)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {
                      'before_update_object': before_update_object,
                      'after_update_object': after_update_object,
                      'before_patch': before_patch
                  }}


class EventRelationship(ResourceRelationship):
    """
    Event Relationship
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query(db, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            view_kwargs['id'] = event.id

    decorators = (api.has_permission('is_coorganizer', fetch="id", fetch_as="event_id",
                                     model=Event),)
    schema = EventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {'before_get_object': before_get_object}
                  }


class EventCopySchema(Schema):
    """
    API Schema for EventCopy
    """

    class Meta:
        """
        Meta class for EventCopySchema
        """
        type_ = 'event-copy'
        inflect = dasherize
        self_view = 'v1.event_copy'
        self_view_kwargs = {'identifier': '<id>'}

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)


class EventCopyResource(ResourceList):
    """
    ResourceList class for EventCopy
    """
    schema = EventCopySchema
    methods = ['POST', ]
    data_layer = {'class': EventCopyLayer,
                  'session': db.Session}


def start_export_tasks(event):
    event_id = str(event.id)
    # XCAL
    from .helpers.tasks import export_xcal_task
    task_xcal = export_xcal_task.delay(event_id, temp=False)
    create_export_job(task_xcal.id, event_id)

    # ICAL
    from .helpers.tasks import export_ical_task
    task_ical = export_ical_task.delay(event_id, temp=False)
    create_export_job(task_ical.id, event_id)

    # PENTABARF XML
    from .helpers.tasks import export_pentabarf_task
    task_pentabarf = export_pentabarf_task.delay(event_id, temp=False)
    create_export_job(task_pentabarf.id, event_id)


def start_image_resizing_tasks(event, original_image_url):
    event_id = str(event.id)
    from .helpers.tasks import resize_event_images_task
    resize_event_images_task.delay(event_id, original_image_url)


def clear_export_urls(event):
    event.ical_url = None
    event.xcal_url = None
    event.pentabarf_url = None
    save_to_db(event)

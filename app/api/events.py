from datetime import datetime

import pytz
from flask import g, request
from flask.blueprints import Blueprint
from flask.json import jsonify
from flask_jwt_extended import current_user, get_jwt_identity, verify_jwt_in_request
from flask_jwt_extended.view_decorators import jwt_optional
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import and_, or_

from app.api.bootstrap import api
from app.api.chat.rocket_chat import (
    RocketChatException,
    get_rocket_chat_token,
    get_rocket_chat_token_virtual_room,
)
from app.api.data_layers.EventCopyLayer import EventCopyLayer
from app.api.helpers.db import safe_query, safe_query_kwargs, save_to_db
from app.api.helpers.errors import (
    ConflictError,
    ForbiddenError,
    NotFoundError,
    UnprocessableEntityError,
)
from app.api.helpers.events import create_custom_forms_for_attendees
from app.api.helpers.export_helpers import create_export_job
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.permissions import jwt_required, to_event_id
from app.api.helpers.utilities import dasherize
from app.api.schema.events import EventSchema, EventSchemaPublic

# models
from app.models import db
from app.models.access_code import AccessCode
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
from app.models.email_notification import EmailNotification
from app.models.event import Event
from app.models.event_copyright import EventCopyright
from app.models.event_invoice import EventInvoice
from app.models.exhibitor import Exhibitor
from app.models.faq import Faq
from app.models.faq_type import FaqType
from app.models.feedback import Feedback
from app.models.group import Group
from app.models.microlocation import Microlocation
from app.models.order import Order
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.social_link import SocialLink
from app.models.speaker import Speaker
from app.models.speaker_invite import SpeakerInvite
from app.models.speakers_call import SpeakersCall
from app.models.sponsor import Sponsor
from app.models.stripe_authorization import StripeAuthorization
from app.models.tax import Tax
from app.models.ticket import Ticket, TicketTag
from app.models.ticket_holder import TicketHolder
from app.models.track import Track
from app.models.user import (
    MARKETER,
    MODERATOR,
    REGISTRAR,
    SALES_ADMIN,
    TRACK_ORGANIZER,
    User,
)
from app.models.user_favourite_event import UserFavouriteEvent
from app.models.users_events_role import UsersEventsRoles
from app.models.video_stream import VideoStream

events_blueprint = Blueprint('events_blueprint', __name__, url_prefix='/v1/events')


@events_blueprint.route('/<string:event_identifier>/has-streams')
@jwt_optional
@to_event_id
def has_streams(event_id):
    event = Event.query.get_or_404(event_id)

    exists = False
    if event.video_stream:
        exists = True
    else:
        exists = db.session.query(
            VideoStream.query.join(VideoStream.rooms)
            .filter(Microlocation.event_id == event.id)
            .exists()
        ).scalar()
    can_access = VideoStream(event_id=event.id).user_can_access
    return jsonify(dict(exists=exists, can_access=can_access))


@events_blueprint.route(
    '/<string:event_identifier>/chat-token',
)
@jwt_required
@to_event_id
def get_chat_token(event_id: int):
    event = Event.query.get_or_404(event_id)

    if not VideoStream(event_id=event.id).user_can_access:
        raise NotFoundError({'source': ''}, 'Video Stream Not Found')

    if not event.is_chat_enabled:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled')

    try:
        data = get_rocket_chat_token(current_user, event)
        return jsonify({'success': True, 'token': data['token']})
    except RocketChatException as rce:
        if rce.code == RocketChatException.CODES.DISABLED:
            return jsonify({'success': False, 'code': rce.code})
        else:
            return jsonify(
                {
                    'success': False,
                    'code': rce.code,
                    'response': rce.response is not None and rce.response.json(),
                }
            )


@events_blueprint.route(
    '/<string:event_identifier>/room/<string:microlocation_id>/chat-token',
)
@jwt_required
@to_event_id
def get_room_chat_token(event_id: int, microlocation_id: int):
    """
    Get room chat token for specific room
    @param event_id: event identifier
    @param microlocation_id: microlocation id
    @return: room chat token
    """
    event = Event.query.get_or_404(event_id)
    microlocation = Microlocation.query.get_or_404(microlocation_id)

    if not VideoStream(event_id=event.id).user_can_access:
        raise NotFoundError({'source': ''}, 'Video Stream Not Found')

    if not event.is_chat_enabled:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled')

    if not microlocation.is_chat_enabled and not microlocation.is_global_event_room:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled For This Room')

    try:
        data = get_rocket_chat_token(current_user, event, microlocation)
        return jsonify({'success': True, 'token': data['token']})
    except RocketChatException as rce:
        if rce.code == RocketChatException.CODES.DISABLED:
            return jsonify({'success': False, 'code': rce.code})
        return jsonify(
            {
                'success': False,
                'code': rce.code,
                'response': rce.response is not None and rce.response.json(),
            }
        )


@events_blueprint.route(
    '/<string:event_identifier>/virtual-room/<int:video_stream_id>/chat-token',
)
@jwt_required
@to_event_id
def get_virtual_room_chat_token(event_id: int, video_stream_id: int):
    """
    Get room chat token for specific room
    @param event_id: event identifier
    @param video_stream_id: microlocation id
    @return: room chat token
    """
    event = Event.query.get_or_404(event_id)
    videoStream = VideoStream.query.get_or_404(video_stream_id)

    if not VideoStream(event_id=event.id).user_can_access:
        raise NotFoundError({'source': ''}, 'Video Stream Not Found')

    if not event.is_chat_enabled:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled')

    if not videoStream.is_chat_enabled and not videoStream.is_global_event_room:
        raise NotFoundError({'source': ''}, 'Chat Not Enabled For This Room')

    try:
        data = get_rocket_chat_token_virtual_room(current_user, event, videoStream)
        return jsonify({'success': True, 'token': data['token']})
    except RocketChatException as rce:
        if rce.code == RocketChatException.CODES.DISABLED:
            return jsonify({'success': False, 'code': rce.code})
        return jsonify(
            {
                'success': False,
                'code': rce.code,
                'response': rce.response is not None and rce.response.json(),
            }
        )


def validate_event(user, data):
    if not user.can_create_event():
        raise ForbiddenError({'source': ''}, "Please verify your Email")

    if data.get('state', None) == Event.State.PUBLISHED and not user.can_publish_event():
        raise ForbiddenError({'source': ''}, "Only verified accounts can publish events")

    if not data.get('name', None) and data.get('state', None) == Event.State.PUBLISHED:
        raise ConflictError(
            {'pointer': '/data/attributes/name'},
            "Event Name is required to publish the event",
        )


def validate_date(event, data):
    if event:
        if 'starts_at' not in data:
            data['starts_at'] = event.starts_at

        if 'ends_at' not in data:
            data['ends_at'] = event.ends_at

    if not data.get('starts_at') or not data.get('ends_at'):
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes/date'},
            "enter required fields starts-at/ends-at",
        )

    if data['starts_at'] >= data['ends_at']:
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at"
        )

    if (data['ends_at'] - data['starts_at']).days > 20:
        raise UnprocessableEntityError(
            {'pointer': '/data/attributes/ends-at'},
            "Event duration can not be more than 20 days",
        )


def get_event_query():
    query_ = Event.query
    if get_jwt_identity() is None or not current_user.is_staff:
        # If user is not admin, we only show published events
        query_ = query_.filter_by(state=Event.State.PUBLISHED)
    if is_logged_in():
        # For a specific user accessing the API, we show all
        # events managed by them, even if they're not published
        verify_jwt_in_request()
        query2 = Event.query
        query2 = (
            query2.join(Event.roles)
            .filter_by(user_id=current_user.id)
            .join(UsersEventsRoles.role)
            .filter(
                or_(
                    Role.name == Role.COORGANIZER,
                    Role.name == Role.ORGANIZER,
                    Role.name == Role.OWNER,
                )
            )
        )
        query_ = query_.union(query2)

    return query_


class EventList(ResourceList):
    def before_get(self, args, kwargs):
        """
        method for assigning schema based on admin access
        :param args:
        :param kwargs:
        :return:
        """
        if is_logged_in() and (has_access('is_admin') or kwargs.get('user_id')):
            self.schema = EventSchema
        else:
            self.schema = EventSchemaPublic

    def query(self, view_kwargs):
        """
        query method for EventList class
        :param view_kwargs:
        :return:
        """
        query_ = get_event_query()

        if view_kwargs.get('user_id') and 'GET' in request.method:
            if not has_access('is_user_itself', user_id=int(view_kwargs['user_id'])):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(Event.roles).filter_by(user_id=user.id)

        if view_kwargs.get('user_owner_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_owner_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_owner_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == Role.OWNER)
            )

        if view_kwargs.get('user_organizer_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_organizer_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_organizer_id')

            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == Role.ORGANIZER)
            )

        if view_kwargs.get('user_coorganizer_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_coorganizer_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_coorganizer_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == Role.COORGANIZER)
            )

        if view_kwargs.get('user_track_organizer_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_track_organizer_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query(
                User,
                'id',
                view_kwargs['user_track_organizer_id'],
                'user_organizer_id',
            )
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == TRACK_ORGANIZER)
            )

        if view_kwargs.get('user_registrar_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_registrar_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_registrar_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == REGISTRAR)
            )

        if view_kwargs.get('user_moderator_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_moderator_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_moderator_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == MODERATOR)
            )

        if view_kwargs.get('user_marketer_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_marketer_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_marketer_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == MARKETER)
            )

        if view_kwargs.get('user_sales_admin_id') and 'GET' in request.method:
            if not has_access(
                'is_user_itself', user_id=int(view_kwargs['user_sales_admin_id'])
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_sales_admin_id')
            query_ = (
                query_.join(Event.roles)
                .filter_by(user_id=user.id)
                .join(UsersEventsRoles.role)
                .filter(Role.name == SALES_ADMIN)
            )

        if view_kwargs.get('event_type_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_type_id') == view_kwargs['event_type_id']
            )

        if view_kwargs.get('event_topic_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_topic_id') == view_kwargs['event_topic_id']
            )

        if view_kwargs.get('event_sub_topic_id') and 'GET' in request.method:
            query_ = self.session.query(Event).filter(
                getattr(Event, 'event_sub_topic_id') == view_kwargs['event_sub_topic_id']
            )

        if view_kwargs.get('discount_code_id') and 'GET' in request.method:
            event_id = get_id(view_kwargs)['id']
            if not has_access('is_coorganizer', event_id=event_id):
                raise ForbiddenError({'source': ''}, 'Coorganizer access is required')
            query_ = self.session.query(Event).filter(
                getattr(Event, 'discount_code_id') == view_kwargs['discount_code_id']
            )

        if view_kwargs.get('group_id') and 'GET' in request.method:
            group = safe_query(Group, 'id', view_kwargs.get('group_id'), 'group_id')
            query_ = self.session.query(Event).filter(
                getattr(Event, 'group_id') == view_kwargs['group_id']
            )

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
        validate_event(user, data)
        if data['state'] != Event.State.DRAFT:
            validate_date(None, data)

    def after_create_object(self, event, data, view_kwargs):
        """
        after create method to save roles for users and add the user as an accepted role(owner and organizer)
        :param event:
        :param data:
        :param view_kwargs:
        :return:
        """
        user = User.query.filter_by(id=view_kwargs['user_id']).first()
        role = Role.query.filter_by(name=Role.OWNER).first()
        uer = UsersEventsRoles(user=user, event=event, role=role)
        save_to_db(uer, 'Event Saved')
        role_invite = RoleInvite(
            email=user.email,
            role_name=role.title_name,
            event=event,
            role=role,
            status='accepted',
        )
        save_to_db(role_invite, 'Owner Role Invite Added')

        # create custom forms for compulsory fields of attendee form.
        create_custom_forms_for_attendees(event)

        if event.state == Event.State.PUBLISHED and event.schedule_published_on:
            start_export_tasks(event)

        if data.get('original_image_url'):
            start_image_resizing_tasks(event, data['original_image_url'])

    # This permission decorator ensures, you are logged in to create an event
    # and have filter ?withRole to get events associated with logged in user
    decorators = (
        api.has_permission(
            'create_event',
        ),
    )
    schema = EventSchema
    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {'after_create_object': after_create_object, 'query': query},
    }


def set_event_id(model, identifier, kwargs, attr='event_id', column_name='id'):
    if kwargs.get('id'):  # ID already set
        return
    if kwargs.get(identifier) is None:
        return
    item = safe_query_kwargs(model, kwargs, identifier, column_name=column_name)
    kwargs['id'] = getattr(item, attr, None)


def get_id(view_kwargs):
    """
    method to get the resource id for fetching details
    :param view_kwargs:
    :return:
    """
    set_event_id(Event, 'identifier', view_kwargs, attr='id', column_name='identifier')

    lookup_list = [
        (Sponsor, 'sponsor_id'),
        (UserFavouriteEvent, 'user_favourite_event_id'),
        (EventCopyright, 'copyright_id'),
        (Track, 'track_id'),
        (SessionType, 'session_type_id'),
        (FaqType, 'faq_type_id'),
        (EventInvoice, 'event_invoice_id'),
        (DiscountCode, 'discount_code_id'),
        (Session, 'session_id'),
        (SocialLink, 'social_link_id'),
        (Tax, 'tax_id'),
        (StripeAuthorization, 'stripe_authorization_id'),
        (DiscountCode, 'discount_code_id'),
        (SpeakersCall, 'speakers_call_id'),
        (Ticket, 'ticket_id'),
        (TicketTag, 'ticket_tag_id'),
        (RoleInvite, 'role_invite_id'),
        (SpeakerInvite, 'speaker_invite_id'),
        (UsersEventsRoles, 'users_events_role_id'),
        (AccessCode, 'access_code_id'),
        (Speaker, 'speaker_id'),
        (EmailNotification, 'email_notification_id'),
        (Microlocation, 'microlocation_id'),
        (TicketHolder, 'attendee_id'),
        (CustomForms, 'custom_form_id'),
        (Faq, 'faq_id'),
        (Feedback, 'feedback_id'),
        (VideoStream, 'video_stream_id'),
        (Exhibitor, 'exhibitor_id'),
    ]
    for model, identifier in lookup_list:
        set_event_id(model, identifier, view_kwargs)

    set_event_id(
        EventInvoice, 'event_invoice_identifier', view_kwargs, column_name='identifier'
    )
    set_event_id(Order, 'order_identifier', view_kwargs, column_name='identifier')

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
        if is_logged_in() and has_access('is_coorganizer', event_id=kwargs['id']):
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

    def after_get_object(self, event, view_kwargs):
        if event and event.state == Event.State.DRAFT:
            if not is_logged_in() or not has_access('is_coorganizer', event_id=event.id):
                raise ObjectNotFound({'parameter': '{id}'}, "Event: not found")

    def before_patch(self, args, kwargs, data=None):
        """
        before patch method to verify if the event location is provided before publishing the event and checks that
        the user is verified
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        user = User.query.filter_by(id=current_user.id).one()
        validate_event(user, data)

    def before_update_object(self, event, data, view_kwargs):
        """
        method to save image urls before updating event object
        :param event:
        :param data:
        :param view_kwargs:
        :return:
        """
        g.event_name = event.name

        is_date_updated = (
            data.get('starts_at') != event.starts_at
            or data.get('ends_at') != event.ends_at
        )
        is_draft_published = (
            event.state == Event.State.DRAFT
            and data.get('state') == Event.State.PUBLISHED
        )
        is_event_restored = event.deleted_at and not data.get('deleted_at')

        if is_date_updated or is_draft_published or is_event_restored:
            validate_date(event, data)

        if data.get('is_document_enabled'):
            d = data.get('document_links')
            if d:
                for document in d:
                    if not document.get('name') or not document.get('link'):
                        raise UnprocessableEntityError(
                            {'pointer': '/'},
                            "Enter required fields link and name",
                        )

        if has_access('is_admin') and data.get('deleted_at') != event.deleted_at:
            if len(event.orders) != 0 and not has_access('is_super_admin'):
                raise ForbiddenError(
                    {'source': ''}, "Event associated with orders cannot be deleted"
                )
            event.deleted_at = data.get('deleted_at')

        if (
            data.get('original_image_url')
            and data['original_image_url'] != event.original_image_url
        ):
            start_image_resizing_tasks(event, data['original_image_url'])
        if data.get('group') != event.group_id:
            if event.is_announced:
                event.is_announced = False
                save_to_db(event)

    def after_update_object(self, event, data, view_kwargs):
        if event.name != g.event_name:
            from .helpers.tasks import rename_chat_room

            rename_chat_room.delay(event.id)

        if event.state == Event.State.PUBLISHED and event.schedule_published_on:
            start_export_tasks(event)
        else:
            clear_export_urls(event)

    decorators = (
        api.has_permission(
            'is_coorganizer',
            methods="PATCH,DELETE",
            fetch="id",
            fetch_as="event_id",
            model=Event,
        ),
    )
    schema = EventSchema
    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {
            'before_update_object': before_update_object,
            'before_get_object': before_get_object,
            'after_get_object': after_get_object,
            'after_update_object': after_update_object,
            'before_patch': before_patch,
        },
    }


class EventRelationship(ResourceRelationship):
    """
    Event Relationship
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query_kwargs(Event, view_kwargs, 'identifier', 'identifier')
            view_kwargs['id'] = event.id

    decorators = (
        api.has_permission(
            'is_coorganizer', fetch="id", fetch_as="event_id", model=Event
        ),
    )
    schema = EventSchema
    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {'before_get_object': before_get_object},
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
    methods = [
        'POST',
    ]
    data_layer = {'class': EventCopyLayer, 'session': db.Session}


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


class UpcomingEventList(EventList):
    """
    List Upcoming Events
    """

    def before_get(self, args, kwargs):
        """
        method for assigning schema based on admin access
        :param args:
        :param kwargs:
        :return:
        """
        super().before_get(args, kwargs)
        self.schema.self_view_many = 'v1.upcoming_event_list'

    def query(self, view_kwargs):
        """
        query method for upcoming events list
        :param view_kwargs:
        :return:
        """
        current_time = datetime.now(pytz.utc)
        query_ = (
            self.session.query(Event)
            .filter(
                Event.starts_at > current_time,
                Event.ends_at > current_time,
                Event.state == Event.State.PUBLISHED,
                Event.privacy == Event.Privacy.PUBLIC,
                or_(
                    Event.is_promoted,
                    and_(
                        Event.is_demoted == False,
                        Event.original_image_url != None,
                        Event.logo_url != None,
                        Event.event_type_id != None,
                        Event.event_topic_id != None,
                        Event.event_sub_topic_id != None,
                        Event.tickets.any(
                            and_(
                                Ticket.deleted_at == None,
                                Ticket.is_hidden == False,
                                Ticket.sales_ends_at > current_time,
                                db.session.query(TicketHolder.id)
                                .join(Order)
                                .filter(
                                    TicketHolder.ticket_id == Ticket.id,
                                    TicketHolder.order_id == Order.id,
                                    TicketHolder.deleted_at.is_(None),
                                )
                                .filter(
                                    or_(
                                        Order.status == 'placed',
                                        Order.status == 'completed',
                                    )
                                )
                                .count()
                                < Ticket.quantity,
                            )
                        ),
                        Event.social_link.any(SocialLink.name == "twitter"),
                    ),
                ),
            )
            .order_by(Event.starts_at)
        )
        return query_

    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {'query': query},
    }

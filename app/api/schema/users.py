from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class UserSchemaPublic(SoftDeletionSchema):
    """
    Api schema for User Model which can be accessed by any resource to which user is related.
    Co-organizers of events to which the user will be related will have access to this info.
    """
    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'user'
        self_view = 'v1.user_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    avatar_url = fields.Url(allow_none=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    original_image_url = fields.Url(dump_only=True, allow_none=True)
    thumbnail_image_url = fields.Url(dump_only=True, allow_none=True)
    small_image_url = fields.Url(dump_only=True, allow_none=True)
    icon_image_url = fields.Url(dump_only=True, allow_none=True)
    was_registered_with_order = fields.Boolean()



class UserSchema(UserSchemaPublic):
    """
    Api schema for User Model
    """
    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'user'
        self_view = 'v1.user_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    facebook_url = fields.Url(allow_none=True)
    twitter_url = fields.Url(allow_none=True)
    instagram_url = fields.Url(allow_none=True)
    google_plus_url = fields.Url(allow_none=True)
    password = fields.Str(required=True, load_only=True)
    is_super_admin = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean()
    facebook_id = fields.Integer(dump_only=True)
    is_sales_admin = fields.Boolean()
    is_marketer = fields.Boolean()
    is_user_organizer = fields.Boolean(dump_only=True)
    is_user_coorganizer = fields.Boolean(dump_only=True)
    is_user_track_organizer = fields.Boolean(dump_only=True)
    is_user_moderator = fields.Boolean(dump_only=True)
    is_user_registrar = fields.Boolean(dump_only=True)
    is_user_attendee = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    last_accessed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    details = fields.Str(allow_none=True)
    contact = fields.Str(allow_none=True)
    notifications = Relationship(
        attribute='notifications',
        self_view='v1.user_notification',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.notification_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='NotificationSchema',
        many=True,
        type_='notification')
    feedbacks = Relationship(
        attribute='feedbacks',
        self_view='v1.user_feedback',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.feedback_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='FeedbackSchema',
        many=True,
        type_='feedback')
    event_invoice = Relationship(
        attribute='event_invoice',
        self_view='v1.user_event_invoice',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_invoice_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='EventInvoiceSchema',
        many=True,
        type_='event-invoice')
    speakers = Relationship(
        attribute='speaker',
        self_view='v1.user_speaker',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.speaker_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='SpeakerSchema',
        many=True,
        type_='speaker')
    access_codes = Relationship(
        attribute='access_codes',
        self_view='v1.user_access_codes',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.access_code_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='AccessCodeSchema',
        type_='access-codes')
    discount_codes = Relationship(
        attribute='discount_codes',
        self_view='v1.user_discount_codes',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.discount_code_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='DiscountCodeSchemaPublic',
        type_='discount-codes')
    email_notifications = Relationship(
        attribute='email_notifications',
        self_view='v1.user_email_notifications',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.email_notification_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='EmailNotificationSchema',
        many=True,
        type_='email-notification')
    alternate_emails = Relationship(
        attribute='alternate_emails',
        self_view='v1.user_emails',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_emails_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='UserEmailSchema',
        many=True,
        type_='user-emails')
    sessions = Relationship(
        attribute='session',
        self_view='v1.user_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='SessionSchema',
        many=True,
        type_='session')
    organizer_events = Relationship(
        self_view='v1.user_organizer_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        many=True,
        type_='event')
    coorganizer_events = Relationship(
        self_view='v1.user_coorganizer_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        many=True,
        type_='event')
    track_organizer_events = Relationship(
        self_view='v1.user_track_organizer_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        many=True,
        type_='event')
    registrar_events = Relationship(
        self_view='v1.user_registrar_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        many=True,
        type_='event')
    moderator_events = Relationship(
        self_view='v1.user_moderator_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        many=True,
        type_='event')
    attendees = Relationship(
        self_view='v1.user_attendees',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.attendee_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='AttendeeSchemaPublic',
        many=True,
        type_='attendee')
    events = Relationship(
        self_view='v1.user_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='EventSchema',
        many=True,
        type_='event')
    favourite_events = Relationship(
        self_view='v1.user_user_favourite_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_favourite_events_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='UserFavouriteEventSchema',
        many=True,
        type_='user-favourite-event')
    orders = Relationship(
        attribute='orders',
        self_view='v1.user_orders',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.orders_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='OrderSchema',
        many=True,
        type_='order')
    marketer_events = Relationship(
        attribute='marketer_events',
        self_view='v1.user_marketer_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        type_='event',
        many=True)
    sales_admin_events = Relationship(
        attribute='sales_admin_events',
        self_view='v1.user_sales_admin_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        schema='EventSchema',
        type_='event',
        many=True)

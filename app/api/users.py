from app.api.bootstrap import api
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.data_layers.VerifyUserLayer import VerifyUserLayer
from app.api.helpers.files import create_save_image_sizes, make_fe_url
from app.api.helpers.mail import send_email_confirmation
from app.api.helpers.utilities import dasherize, get_serializer, str_generator
from app.models import db
from app.models.user import User
from app.models.notification import Notification
from app.models.users_events_role import UsersEventsRoles
from app.models.email_notification import EmailNotification
from app.models.event_invoice import EventInvoice
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.api.helpers.permissions import is_user_itself, jwt_required
from app.models.speaker import Speaker
from app.api.helpers.exceptions import ConflictException
from app.api.helpers.db import safe_query


class UserSchema(Schema):
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

    id = fields.Str(dump_only=True)
    email = fields.Email(required=True)
    password = fields.Str(required=True, load_only=True)
    avatar_url = fields.Url(allow_none=True)
    is_super_admin = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    last_accessed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    first_name = fields.Str(allow_none=True)
    last_name = fields.Str(allow_none=True)
    details = fields.Str(allow_none=True)
    contact = fields.Str(allow_none=True)
    facebook_url = fields.Url(allow_none=True)
    twitter_url = fields.Url(allow_none=True)
    instagram_url = fields.Url(allow_none=True)
    google_plus_url = fields.Url(allow_none=True)
    original_image_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(dump_only=True, allow_none=True)
    small_image_url = fields.Url(dump_only=True, allow_none=True)
    icon_image_url = fields.Url(dump_only=True, allow_none=True)
    notification = Relationship(
        attribute='notification',
        self_view='v1.user_notification',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.notification_list',
        related_view_kwargs={'user_id': '<id>'},
        schema='NotificationSchema',
        many=True,
        type_='notification')
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
        schema='DiscountCodeSchema',
        type_='discount-codes')
    email_notifications = Relationship(
        attribute='email_notifications',
        self_view='v1.user_email_notifications',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.email_notification_list',
        related_view_kwargs={'id': '<id>'},
        schema='EmailNotificationSchema',
        many=True,
        type_='email-notification')


class UserList(ResourceList):
    """
    List and create Users
    """
    def before_create_object(self, data, view_kwargs):
        if db.session.query(User.id).filter_by(email=data['email']).scalar() is not None:
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

    def after_create_object(self, user, data, view_kwargs):
        s = get_serializer()
        hash = s.dumps([user.email, str_generator()])
        link = make_fe_url(path='/email/verify?token={token}'.format(token=hash))
        send_email_confirmation(user.email, link)
        if data.get('original_image_url'):
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'user', user.id)
            uploaded_images['small_image_url'] = uploaded_images['thumbnail_image_url']
            del uploaded_images['large_image_url']
            self.session.query(User).filter_by(id=user.id).update(uploaded_images)


    decorators = (api.has_permission('is_admin', methods="GET"),)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method for user object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('notification_id') is not None:
            notification = safe_query(self, Notification, 'id', view_kwargs['notification_id'], 'notification_id')
            if notification.user_id is not None:
                view_kwargs['id'] = notification.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_id') is not None:
            event_invoice = safe_query(self, EventInvoice, 'id', view_kwargs['event_invoice_id'], 'event_invoice_id')
            if event_invoice.user_id is not None:
                view_kwargs['id'] = event_invoice.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
            users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
            'users_events_role_id')
            if users_events_role.user_id is not None:
                view_kwargs['id'] = users_events_role.user_id

        if view_kwargs.get('speaker_id') is not None:
            speaker = safe_query(self, Speaker, 'id', view_kwargs['speaker_id'], 'speaker_id')
            if speaker.user_id is not None:
                view_kwargs['id'] = speaker.user_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('access_code_id') is not None:
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            if access_code.marketer_id is not None:
                view_kwargs['id'] = access_code.marketer_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('discount_code_id') is not None:
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            if discount_code.marketer_id is not None:
                view_kwargs['id'] = discount_code.marketer_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('email_notification_id') is not None:
            email_notification = safe_query(self, EmailNotification, 'id', view_kwargs['email_notification_id'], 'email_notification_id')
            if email_notification.user_id is not None:
                view_kwargs['id'] = email_notification.user_id
            else:
                view_kwargs['id'] = None

    def before_update_object(self, user, data, view_kwargs):
        if data.get('original_image_url') and data['original_image_url'] != user.original_image_url:
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'user', user.id)
            data['original_image_url'] = uploaded_images['original_image_url']
            data['small_image_url'] = uploaded_images['thumbnail_image_url']
            data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
            data['icon_image_url'] = uploaded_images['icon_image_url']
        else:
            if data.get('small_image_url'):
                del data['small_image_url']
            if data.get('thumbnail_image_url'):
                del data['thumbnail_image_url']
            if data.get('icon_image_url'):
                del data['icon_image_url']

    decorators = (api.has_permission('is_user_itself', fetch="user_id,id", fetch_as="id",
                  model=[Notification, UsersEventsRoles, EventInvoice, AccessCode,
                         DiscountCode, EmailNotification, User],
                  fetch_key_url="notification_id, users_events_role_id,\
                  event_invoice_id, access_code_id, discount_code_id, email_notification_id, id"),)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object
                  }}


class UserRelationship(ResourceRelationship):

    decorators = (jwt_required, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


class VerifyUserSchema(Schema):
    class Meta:
        """
        Meta class for Verify User Schema
        """
        type_ = 'verify-user'
        self_view = 'v1.verify_user'
        self_view_kwargs = {'user_id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    token = fields.Str(required=True)


class VerifyUser(ResourceList):

    methods = ['POST', ]
    decorators = (jwt_required,)
    schema = VerifyUserSchema
    data_layer = {
        'class': VerifyUserLayer,
        'session': db.session
    }

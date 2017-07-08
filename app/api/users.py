from app.api.bootstrap import api
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.user import User
from app.models.notification import Notification
from app.models.users_events_role import UsersEventsRoles
from app.models.event_invoice import EventInvoice
from app.api.helpers.permissions import is_user_itself, jwt_required
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
        self_view_many = 'v1.user_list'
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
    thumbnail_image_url = fields.Url(attribute='thumbnail_image_url', allow_none=True)
    small_image_url = fields.Url(attribute='small_image_url', allow_none=True)
    icon_image_url = fields.Url(attribute='icon_image_url', allow_none=True)
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


class UserList(ResourceList):
    """
    List and create Users
    """
    def before_create_object(self, data, view_kwargs):
        if db.session.query(User.id).filter_by(email=data['email']).scalar() is not None:
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

    decorators = (api.has_permission('is_admin', methods="GET"),)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {'before_create_object': before_create_object}}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """

    def before_get_object(self, view_kwargs):
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
            else:
                view_kwargs['id'] = None

    decorators = (is_user_itself, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {'before_get_object': before_get_object}}


class UserRelationship(ResourceRelationship):

    decorators = (jwt_required, )
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

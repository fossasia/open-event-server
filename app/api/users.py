from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from sqlalchemy.orm.exc import NoResultFound
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.user import User
from app.models.notification import Notification
from app.models.event_invoice import EventInvoice
from app.models.event import Event
from app.api.helpers.permissions import is_admin, is_user_itself, jwt_required


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
    avatar = fields.Str()
    is_super_admin = fields.Boolean(dump_only=True)
    is_admin = fields.Boolean(dump_only=True)
    is_verified = fields.Boolean(dump_only=True)
    signup_at = fields.DateTime(dump_only=True)
    last_accessed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)
    firstname = fields.Str()
    lastname = fields.Str()
    details = fields.Str()
    contact = fields.Str()
    facebook = fields.Str()
    twitter = fields.Str()
    instagram = fields.Str()
    google = fields.Str()
    avatar_uploaded = fields.Str()
    thumbnail_url = fields.Url(attribute='thumbnail')
    small_url = fields.Url(attribute='small')
    icon_url = fields.Url(attribute='icon')
    notification = Relationship(attribute='notification',
                                self_view='v1.user_notification',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.notification_list',
                                related_view_kwargs={'user_id': '<id>'},
                                schema='NotificationSchema',
                                many=True,
                                type_='notification')
    event_invoice = Relationship(attribute='event_invoice',
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
    get = is_admin(ResourceList.get.__func__)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}


class UserDetail(ResourceDetail):
    """
    User detail by id
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('notification_id'):
            try:
                notification = self.session.query(Notification).filter_by(
                    id=view_kwargs['notification_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'notification_id'},
                                     "Notification: {} not found".format(view_kwargs['notification_id']))
            else:
                if notification.user_id is not None:
                    view_kwargs['id'] = notification.user_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('event_invoice_id'):
            try:
                event_invoice = self.session.query(EventInvoice).filter_by(
                    id=view_kwargs['event_invoice_id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': 'event_invoice_id'},
                                     "Event Invoice: {} not found".format(view_kwargs['event_invoice_id']))
            else:
                if event_invoice.user_id is not None:
                    view_kwargs['id'] = event_invoice.user_id
                else:
                    view_kwargs['id'] = None

    decorators = (is_user_itself,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User,
                  'methods': {'before_get_object': before_get_object}}


class UserRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = UserSchema
    data_layer = {'session': db.session,
                  'model': User}

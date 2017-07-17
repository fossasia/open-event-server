from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.email_notification import EmailNotification
from app.models.user import User
from app.api.helpers.permissions import is_user_itself, jwt_required
from app.api.helpers.db import safe_query


class EmailNotificationSchema(Schema):
    """
    API Schema for email notification Model
    """

    class Meta:
        """
        Meta class for email notification API schema
        """
        type_ = 'email-notification'
        self_view = 'v1.email_notification_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    next_event = fields.Integer(default=0, allow_none=True)
    new_paper = fields.Integer(default=0, allow_none=True)
    session_accept_reject = fields.Integer(default=0, allow_none=True)
    session_schedule = fields.Integer(default=0, allow_none=True)
    after_ticket_purchase = fields.Integer(default=0, allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.email_notification_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'email_notification_id': '<id>'},
                         schema='EventSchema',
                         type_='event'
                         )
    user = Relationship(attribute='user',
                        self_view='v1.email_notification_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'email_notification_id': '<id>'},
                        schema='UserSchema',
                        type_='user'
                        )

class EmailNotificationList(ResourceList):
    """
    List all the email notification
    """

    def query(self, view_kwargs):
        """
        query method for Notifications list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(EmailNotification)
        if view_kwargs.get('id'):
            user = safe_query(self, User, 'id', view_kwargs['id'], 'id')
            query_ = query_.join(User).filter(User.id == user.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('id') is not None:
            user = safe_query(self, User, 'id', view_kwargs['id'], 'id')
            data['user_id'] = user.id

    view_kwargs = True
    decorators = (is_user_itself,)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class EmailNotificationDetail(ResourceDetail):
    """
    Email notification detail by ID
    """
    decorators = (is_user_itself,)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}


class EmailNotificationRelationship(ResourceRelationship):
    """
    Email notification Relationship
    """
    decorators = (jwt_required,)
    schema = EmailNotificationSchema
    data_layer = {'session': db.session,
                  'model': EmailNotification}

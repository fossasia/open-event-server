from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class NotificationActionSchema(SoftDeletionSchema):
    """
    API Schema for NotificationAction Model
    """

    class Meta:
        """
        Meta class for Notification Action API schema
        """
        type_ = 'notification-action'
        self_view = 'v1.notification_action_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    action_type = fields.Str(allow_none=True, dump_only=True)
    subject = fields.Str(allow_none=True, dump_only=True)
    subject_id = fields.Str(allow_none=True, dump_only=True)
    notification_id = fields.Str(allow_none=True, dump_only=True)
    link = fields.Str(dump_only=True)
    notification = Relationship(attribute='notification',
                                self_view='v1.notification_actions_notification',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.notification_detail',
                                related_view_kwargs={'notification_action_id': '<id>'},
                                schema='NotificationSchema',
                                type_='notification-action')


class NotificationSchema(SoftDeletionSchema):
    """
    API Schema for Notification Model
    """

    class Meta:
        """
        Meta class for Notification API schema
        """
        type_ = 'notification'
        self_view = 'v1.notification_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    title = fields.Str(allow_none=True, dump_only=True)
    message = fields.Str(allow_none=True, dump_only=True)
    received_at = fields.DateTime(dump_only=True)
    accept = fields.Str(allow_none=True, dump_only=True)
    is_read = fields.Boolean()
    notification_actions = Relationship(attribute='actions',
                                        schema='NotificationActionSchema',
                                        self_view='v1.notification_actions',
                                        self_view_kwargs={'id': '<id>'},
                                        related_view='v1.notification_actions_list',
                                        related_view_kwargs={'notification_id': '<id>'},
                                        many=True,
                                        type_='notification-action')
    user = Relationship(attribute='user',
                        self_view='v1.notification_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'notification_id': '<id>'},
                        schema='UserSchema',
                        type_='user')

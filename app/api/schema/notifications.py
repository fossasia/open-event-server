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
        type_ = 'notification_action'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    action_type = fields.Str(allow_none=True, dump_only=True)
    subject = fields.Str(allow_none=True, dump_only=True)
    subject_id = fields.Str(allow_none=True, dump_only=True)


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
        self_view_many = 'v1.microlocation_list_post'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    title = fields.Str(allow_none=True, dump_only=True)
    message = fields.Str(allow_none=True, dump_only=True)
    received_at = fields.DateTime(dump_only=True)
    accept = fields.Str(allow_none=True, dump_only=True)
    is_read = fields.Boolean()
    actions = fields.List(cls_or_instance=fields.Nested(NotificationActionSchema), allow_none=True, dump_only=True)
    user = Relationship(attribute='user',
                        self_view='v1.notification_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'notification_id': '<id>'},
                        schema='UserSchema',
                        type_='user')

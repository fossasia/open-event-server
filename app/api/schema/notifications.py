from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize


class NotificationSchema(Schema):
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
    created_at = fields.DateTime(dump_only=True)
    is_read = fields.Boolean()
    user = Relationship(
        self_view='v1.notification_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'notification_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )

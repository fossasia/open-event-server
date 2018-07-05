from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class EmailNotificationSchema(SoftDeletionSchema):
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

    id = fields.Integer(dump_only=True)
    next_event = fields.Boolean(default=False, allow_none=True)
    new_paper = fields.Boolean(default=False, allow_none=True)
    session_accept_reject = fields.Boolean(default=False, allow_none=True)
    session_schedule = fields.Boolean(default=False, allow_none=True)
    after_ticket_purchase = fields.Boolean(default=True, allow_none=True)
    event_id = fields.Integer(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.email_notification_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'email_notification_id': '<id>'},
                         schema='EventSchemaPublic',
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

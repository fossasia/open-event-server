from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from marshmallow import validate

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class SessionChatMessageSchema(SoftDeletionSchema):
    """
    Api schema for Session Chat Message Model
    """

    class Meta:
        """
        Meta class for Session Chat Message Api Schema
        """
        type_ = 'session-chat-message'
        self_view = 'v1.session_chat_message_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    message = fields.Str(required=True)
    sent_at = fields.DateTime(dump_only=True)
    timezone = fields.Str(required=True)
    label = fields.Str(validate=validate.OneOf(choices=["Speaker", "Attendee"]),
                       allow_none=True)
    session = Relationship(attribute='session',
                           self_view='v1.session_chat_message_session',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.session_detail',
                           related_view_kwargs={'session_message_id': '<id>'},
                           schema='SessionSchema',
                           type_='session')
    user = Relationship(attribute='user',
                        self_view='v1.session_chat_message_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'session_message_id': '<id>'},
                        schema='UserSchema',
                        type_='user')

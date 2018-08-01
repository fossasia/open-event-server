from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from marshmallow import validate

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class EventChatMessageSchema(SoftDeletionSchema):
    """
    Api schema for Event Chat Message Model
    """

    class Meta:
        """
        Meta class for Session Api Schema
        """
        type_ = 'event-chat-message'
        self_view = 'v1.event_chat_message_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    message = fields.Str(required=True)
    sent_at = fields.DateTime(dump_only=True)
    timezone = fields.Str(required=True)
    label = fields.Str(validate=validate.OneOf(choices=["Organizer", "Co-organizer", "Track Organizer",
                       "Moderator",  "Registrar", "Speaker", "Attendee"]), allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.event_chat_message_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'message_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    user = Relationship(attribute='user',
                        self_view='v1.event_chat_message_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'message_id': '<id>'},
                        schema='UserSchema',
                        type_='user')

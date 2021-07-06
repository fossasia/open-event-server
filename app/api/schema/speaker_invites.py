from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import TrimmedEmail
from utils.common import use_defaults


@use_defaults()
class SpeakerInviteSchema(Schema):
    """
    Public Api Schema for speaker invite model
    """

    class Meta:
        """
        Meta class for speaker invite public Api Schema
        """

        type_ = 'speaker-invite'
        self_view = 'v1.speaker_invite_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    email = TrimmedEmail(required=True)
    status = fields.Str(
        validate=validate.OneOf(choices=["pending", "accepted", "rejected"]),
        default="pending",
    )
    session = Relationship(
        self_view='v1.speaker_invite_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_detail',
        related_view_kwargs={'speaker_invite_id': '<id>'},
        schema='SessionSchema',
        type_='session',
    )
    event = Relationship(
        self_view='v1.speaker_invite_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'speaker_invite_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

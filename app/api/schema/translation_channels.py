from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class TranslationChannelSchema(Schema):
    """Schema of Translation Channel objects"""

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    url = fields.String(required=True)

    video_stream = Relationship(
        self_view="v1.translation_channels_video_stream",
        self_view_kwargs={"id": "<id>"},
        related_view="v1.video_stream_detail",
        related_view_kwargs={"id": "<video_stream_id>"},
        schema="VideoStreamSchema",
        type_="video_stream",
    )

    channel = Relationship(
        self_view="v1.translation_channels_channel",
        self_view_kwargs={"id": "<id>"},
        related_view="v1.video_channel_detail",
        related_view_kwargs={"id": "<channel_id>"},
        schema="VideoChannelSchema",
        type_="video_channel",
    )

    class Meta:
        type_ = "translation_channel"
        self_view = 'v1.translation_channels_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.translation_channels_list'
        inflect = dasherize
        strict = True

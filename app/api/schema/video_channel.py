from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.fields import CustomFormValueField
from app.api.helpers.utilities import dasherize


class VideoChannelSchemaPublic(Schema):
    class Meta:
        type_ = 'video-channel'
        self_view = 'v1.video_channel_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    provider = fields.Str(required=True)
    url = fields.Url(required=True)
    api_url = fields.Url(required=False, allow_none=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)


class VideoChannelSchema(VideoChannelSchemaPublic):
    class Meta:
        type_ = 'video-channel'
        self_view = 'v1.video_channel_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    api_key = fields.Str(allow_none=True)
    extra = CustomFormValueField(allow_none=True)

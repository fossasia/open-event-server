from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class VideoStreamSchema(Schema):
    class Meta:
        type_ = 'video-stream'
        self_view = 'v1.video_stream_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Url(required=True)
    password = fields.Str(required=False, allow_none=True)
    additional_information = fields.Str(required=False, allow_none=True)
    rooms = Relationship(
        many=True,
        self_view='v1.video_stream_rooms',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.microlocation_list',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='MicrolocationSchema',
        type_='microlocation',
    )

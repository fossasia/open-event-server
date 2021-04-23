from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from marshmallow_jsonapi.flask import Schema as JSONAPISchema

from app.api.helpers.utilities import dasherize


class VideoRecordingSchema(JSONAPISchema):
    class Meta:
        type_ = 'video-recording'
        self_view = 'v1.video_recording_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    bbb_record_id = fields.Str()
    participants = fields.Integer(required=True)
    url = fields.Url(required=True)
    start_time = fields.DateTime(required=True, timezone=False)
    end_time = fields.DateTime(required=True, timezone=False)

    video_stream = Relationship(
        self_view='v1.video_recording_stream',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_stream_detail',
        related_view_kwargs={'video_recording_id': '<id>'},
        schema='VideoStreamSchema',
        type_='video-stream',
    )

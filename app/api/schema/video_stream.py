from marshmallow import Schema as JsonSchema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class VideoStreamExtraOptionsSchema(JsonSchema):
    record = fields.Boolean(default=True)
    autoStartRecording = fields.Boolean(default=False)
    muteOnStart = fields.Boolean(default=True)
    welcome = fields.String(required=False, allow_none=True)
    maxParticipants = fields.Integer(required=False, allow_none=True)
    duration = fields.Integer(required=False, allow_none=True)
    moderatorOnlyMessage = fields.String(required=False, allow_none=True)
    logo = fields.URL(required=False, allow_none=True)
    bannerText = fields.String(required=False, allow_none=True)
    bannerColor = fields.String(required=False, allow_none=True)
    guestPolicy = fields.String(required=False, allow_none=True)
    allowModsToUnmuteUsers = fields.Boolean(default=True)
    endCurrentMeeting = fields.Boolean(default=False)


class VideoStreamJitsiOptionsSchema(JsonSchema):
    muteOnStart = fields.Boolean(default=False)
    hideCamOnStart = fields.Boolean(default=False)


class VideoStreamExtraSchema(JsonSchema):
    autoplay = fields.Boolean(default=True)
    loop = fields.Boolean(default=False)
    bbb_options = fields.Nested(VideoStreamExtraOptionsSchema, allow_none=True)
    jitsi_options = fields.Nested(VideoStreamJitsiOptionsSchema, allow_none=True)


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
    bg_img_url = fields.Str(required=False, allow_none=True)
    additional_information = fields.Str(required=False, allow_none=True)
    extra = fields.Nested(VideoStreamExtraSchema, allow_none=True)
    rooms = Relationship(
        many=True,
        self_view='v1.video_stream_rooms',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.microlocation_list',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='MicrolocationSchema',
        type_='microlocation',
    )
    event = Relationship(
        self_view='v1.video_stream_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    video_channel = Relationship(
        attribute='channel',
        self_view='v1.video_stream_channel',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_channel_detail',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='VideoChannelSchemaPublic',
        type_='video-channel',
    )
    video_recordings = Relationship(
        many=True,
        self_view='v1.video_stream_recordings',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_recording_list',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='VideoRecordingSchema',
        type_='video-recording',
    )
    moderators = Relationship(
        many=True,
        self_view='v1.video_stream_moderators',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_stream_moderator_list',
        related_view_kwargs={'video_stream_id': '<id>'},
        schema='VideoStreamModeratorSchema',
        type_='video-stream-moderator',
    )


class ChatmosphereSchema(Schema):
    class Meta:
        type_ = 'video-stream'
        self_view = 'v1.video_stream_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    url = fields.Url(required=True)
    bg_img_url = fields.Str(required=False, allow_none=True)

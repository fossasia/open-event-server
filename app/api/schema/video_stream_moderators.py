from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class VideoStreamModeratorSchema(SoftDeletionSchema):
    """
    Api schema for users_events_role Model
    """

    class Meta:
        """
        Meta class for users_events_role Api Schema
        """

        type_ = 'video-stream-moderator'
        self_view = 'v1.video_stream_moderator_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)

    event = Relationship(
        self_view='v1.video_stream_moderator_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'video_stream_moderator_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

    video_stream = Relationship(
        many=True,
        self_view='v1.video_stream_moderator_stream',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_stream_detail',
        related_view_kwargs={'video_stream_moderator_id': '<id>'},
        schema='VideoStreamSchema',
        type_="video-stream",
    )

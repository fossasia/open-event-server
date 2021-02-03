from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class VideoStreamModeratorSchema(SoftDeletionSchema):
    """
    Api schema for video_stream_moderator Model
    """

    class Meta:
        """
        Meta class for video_stream_moderator Api Schema
        """

        type_ = 'video-stream-moderator'
        self_view = 'v1.video_stream_moderator_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    deleted_at = fields.DateTime(dump_only=True)

    user = Relationship(
        self_view='v1.video_stream_moderator_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'video_stream_moderator_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
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

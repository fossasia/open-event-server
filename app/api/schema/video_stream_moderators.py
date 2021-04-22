from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import TrimmedEmail


class VideoStreamModeratorSchema(Schema):
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
    email = TrimmedEmail(required=True)

    user = Relationship(
        dumps_only=True,
        self_view='v1.video_stream_moderator_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'video_stream_moderator_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
    )

    video_stream = Relationship(
        self_view='v1.video_stream_moderator_stream',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.video_stream_detail',
        related_view_kwargs={'video_stream_moderator_id': '<id>'},
        schema='VideoStreamSchema',
        type_="video-stream",
    )

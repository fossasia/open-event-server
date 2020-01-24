from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class EventImageSizeSchema(Schema):
    """
    Api schema for image_size Model
    """

    class Meta:
        """
        Meta class for image_size Api Schema
        """

        type_ = 'event-image-size'
        self_view = 'v1.event_image_size_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    type = fields.Str(allow_none=True)
    full_width = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    full_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    full_aspect = fields.Boolean(default=False)
    full_quality = fields.Integer(validate=lambda n: 0 <= n <= 100, allow_none=True)
    icon_width = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    icon_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    icon_aspect = fields.Boolean(default=False)
    icon_quality = fields.Integer(validate=lambda n: 0 <= n <= 100, allow_none=True)
    thumbnail_width = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    thumbnail_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    thumbnail_aspect = fields.Boolean(default=False)
    thumbnail_quality = fields.Integer(validate=lambda n: 0 <= n <= 100, allow_none=True)
    logo_width = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    logo_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)


@use_defaults()
class SpeakerImageSizeSchema(Schema):
    """
    Api schema for image_size Model
    """

    class Meta:
        """
        Meta class for image_size Api Schema
        """

        type_ = 'speaker-image-size'
        self_view = 'v1.speaker_image_size_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    type = fields.Str(allow_none=True)
    small_size_width_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    small_size_quality = fields.Integer(validate=lambda n: 0 <= n <= 100, allow_none=True)
    thumbnail_size_width_height = fields.Integer(
        validate=lambda n: n >= 0, allow_none=True
    )
    thumbnail_size_quality = fields.Integer(
        validate=lambda n: 0 <= n <= 100, allow_none=True
    )
    icon_size_width_height = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    icon_size_quality = fields.Integer(validate=lambda n: 0 <= n <= 100, allow_none=True)

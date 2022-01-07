from marshmallow import validate, validates_schema
from marshmallow.schema import Schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.fields import CustomFormValueField
from app.api.helpers.static import GENDER_CHOICES
from app.api.helpers.utilities import dasherize
from app.api.helpers.validations import validate_complex_fields_json
from app.api.schema.base import SoftDeletionSchema, TrimmedEmail
from utils.common import use_defaults


@use_defaults()
class SpeakerSchema(SoftDeletionSchema):
    """
    Speaker Schema based on Speaker Model
    """

    @validates_schema(pass_original=True)
    def validate_json(self, data, original_data):
        validate_complex_fields_json(self, data, original_data)

    class Meta:
        """
        Meta class for speaker schema
        """

        type_ = 'speaker'
        self_view = 'v1.speaker_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    email = TrimmedEmail(allow_none=True)
    photo_url = fields.Url(allow_none=True)
    thumbnail_image_url = fields.Url(allow_none=True)
    small_image_url = fields.Url(allow_none=True)
    icon_image_url = fields.Url(allow_none=True)
    short_biography = fields.Str(allow_none=True)
    long_biography = fields.Str(allow_none=True)
    speaking_experience = fields.Str(allow_none=True)
    mobile = fields.Str(allow_none=True)
    website = fields.Url(allow_none=True)
    twitter = fields.Url(allow_none=True)
    facebook = fields.Url(allow_none=True)
    github = fields.Url(allow_none=True)
    mastodon = fields.Url(allow_none=True)
    linkedin = fields.Url(allow_none=True)
    instagram = fields.Url(allow_none=True)
    organisation = fields.Str(allow_none=True)
    is_featured = fields.Boolean(default=False)
    is_email_overridden = fields.Boolean(default=False)
    position = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True, validate=validate.OneOf(choices=GENDER_CHOICES))
    order = fields.Integer(allow_none=True, default=0)
    heard_from = fields.Str(allow_none=True)
    sponsorship_required = fields.Str(allow_none=True)
    complex_field_values = CustomFormValueField(allow_none=True)
    speaker_positions = CustomFormValueField(allow_none=True)

    event = Relationship(
        self_view='v1.speaker_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'speaker_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    user = Relationship(
        self_view='v1.speaker_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'speaker_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
        dump_only=True,
    )
    sessions = Relationship(
        self_view='v1.speaker_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_list',
        related_view_kwargs={'speaker_id': '<id>'},
        schema='SessionSchema',
        many=True,
        type_='session',
    )


class SpeakerReorderSchema(Schema):
    speaker = fields.Integer(required=True)
    order = fields.Integer(required=True)

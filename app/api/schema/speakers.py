from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class SpeakerSchema(SoftDeletionSchema):
    """
    Speaker Schema based on Speaker Model
    """

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
    email = fields.Str(required=True)
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
    linkedin = fields.Url(allow_none=True)
    organisation = fields.Str(allow_none=True)
    is_featured = fields.Boolean(default=False)
    position = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    gender = fields.Str(allow_none=True)
    heard_from = fields.Str(allow_none=True)
    sponsorship_required = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.speaker_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'speaker_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    user = Relationship(attribute='user',
                        self_view='v1.speaker_user',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'speaker_id': '<id>'},
                        schema='UserSchemaPublic',
                        type_='user')
    sessions = Relationship(attribute='sessions',
                            self_view='v1.speaker_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'speaker_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')

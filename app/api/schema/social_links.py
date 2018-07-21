from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class SocialLinkSchema(SoftDeletionSchema):
    """
    Social Link API Schema based on Social link model
    """
    class Meta:
        """
        Meta class for social link schema
        """
        type_ = 'social-link'
        self_view = 'v1.social_link_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    link = fields.Url(required=True)
    identifier = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.social_link_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'social_link_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

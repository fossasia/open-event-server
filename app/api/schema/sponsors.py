from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class SponsorSchema(SoftDeletionSchema):
    """
    Sponsors API schema based on Sponsors model
    """

    class Meta:
        """
        Meta class for Sponsor schema
        """

        type_ = 'sponsor'
        self_view = 'v1.sponsor_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    url = fields.Url(allow_none=True)
    level = fields.Integer(allow_none=True)
    logo_url = fields.Url(allow_none=True)
    type = fields.Str(allow_none=True)
    event = Relationship(
        self_view='v1.sponsor_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'sponsor_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

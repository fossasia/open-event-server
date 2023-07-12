from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.custom.schema.badge_form_field import BadgeFieldFormSchema
from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class BadgeFormSchema(Schema):
    """API Schema for Badge Form database model"""

    class Meta:
        """Meta class for Badge Form Schema"""

        type_ = 'badge-form'
        self_view = 'v1.badge_form_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    badge_id = fields.String(allow_none=False)
    badge_size = fields.String(allow_none=True)
    badge_color = fields.String(allow_none=True)
    badge_image_url = fields.String(allow_none=True)
    badge_orientation = fields.String(allow_none=True)
    event = Relationship(
        self_view='v1.badge_form_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'badge_form_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    badge_fields = fields.Nested(BadgeFieldFormSchema, many=True)

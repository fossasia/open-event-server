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
    badge_id = fields.Str(required=True)
    badge_size = fields.Str(required=False)
    badge_color = fields.Str(required=False)
    badge_image_url = fields.Str(required=False)
    badge_orientation = fields.Str(required=False)
    event = Relationship(
        self_view='v1.badge_form_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'badge_form_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    badge_fields = fields.Nested(BadgeFieldFormSchema, many=True)

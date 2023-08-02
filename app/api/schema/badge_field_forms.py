from marshmallow.schema import Schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


class FontWeight(Schema):
    name = fields.String(required=False)
    font_weight = fields.String(required=False)
    font_style = fields.String(required=False)
    text_decoration = fields.String(required=False)


@use_defaults()
class BadgeFieldFormSchema(Schema):
    """API Schema for Badge Field Forms database model"""

    class Meta:
        """Meta class for Badge Field Form Schema"""

        type_ = 'badge-field-form'
        self_view = 'v1.badge_field_form_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    badge_field_id = fields.Integer(dump_only=True)
    badge_form = Relationship(
        self_view='v1.badge_field_form_badge_form',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.badge_form_detail',
        related_view_kwargs={'badge_field_form_id': '<id>'},
        schema='BadgeFormSchema',
        type_='badge_form',
    )
    badge_id = fields.Str(required=True)
    field_identifier = fields.String(required=False)
    custom_field = fields.String(required=False)
    sample_text = fields.String(required=False)
    font_size = fields.Integer(required=False)
    text_alignment = fields.String(required=False)
    text_type = fields.String(required=False)
    is_deleted = fields.Boolean(required=False, default=False)
    font_name = fields.String(required=False)
    font_weight = fields.List(fields.Nested(FontWeight), allow_none=True, required=False)
    font_color = fields.String(required=False)
    margin_top = fields.Integer(required=False)
    margin_bottom = fields.Integer(required=False)
    margin_left = fields.Integer(required=False)
    margin_right = fields.Integer(required=False)
    text_rotation = fields.Integer(required=False)
    qr_custom_field = fields.List(fields.String(), required=False)
    is_field_expanded = fields.Boolean(required=False, default=False)

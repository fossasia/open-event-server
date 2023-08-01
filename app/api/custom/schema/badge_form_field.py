from marshmallow import Schema, fields

from app.api.schema.badge_field_forms import FontWeight


class BadgeFieldFormSchema(Schema):
    """Badge Field Form Schema"""

    badge_field_id = fields.Integer(allow_none=False)
    badge_id = fields.String(allow_none=False)
    field_identifier = fields.String(allow_none=True)
    custom_field = fields.String(allow_none=True)
    sample_text = fields.String(allow_none=True)
    font_size = fields.Integer(allow_none=True)
    font_name = fields.String(allow_none=True)
    font_weight = fields.List(fields.Nested(FontWeight), allow_none=True)
    font_color = fields.String(allow_none=True)
    text_rotation = fields.Integer(allow_none=True)
    text_alignment = fields.String(allow_none=True)
    text_type = fields.String(allow_none=True)
    badge_field_id = fields.Integer(allow_none=True)
    is_deleted = fields.Boolean(allow_none=True, default=False)
    margin_top = fields.Integer(allow_none=True)
    margin_bottom = fields.Integer(allow_none=True)
    margin_left = fields.Integer(allow_none=True)
    margin_right = fields.Integer(allow_none=True)
    qr_custom_field = fields.List(fields.String(), allow_none=True, default=None)
    is_field_expanded = fields.Boolean(allow_none=True, default=True)

from marshmallow import Schema, fields


class BadgeFieldFormSchema(Schema):
    """Badge Field Form Schema"""

    badge_id = fields.String(required=True)
    custom_field = fields.String(required=False)
    sample_text = fields.String(required=False)
    font_size = fields.Integer(required=False)
    font_name = fields.String(required=False)
    font_weight = fields.String(required=False)
    font_color = fields.String(required=False)
    text_rotation = fields.Integer(required=False)
    text_alignment = fields.String(required=False)
    text_type = fields.String(required=False)
    id = fields.Integer(required=False)
    is_deleted = fields.Boolean(required=False, default=False)
    margin_top = fields.Integer(required=False)
    margin_bottom = fields.Integer(required=False)
    margin_left = fields.Integer(required=False)
    margin_right = fields.Integer(required=False)
    qr_custom_field = fields.String(required=False)

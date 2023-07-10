from marshmallow import Schema, fields


class BadgeFieldFormSchema(Schema):
    """Badge Field Form Schema"""

    badge_id = fields.String(required=True)
    custom_field = fields.String(required=False)
    sample_text = fields.String(required=False)
    font_size = fields.Integer(required=False)
    text_alignment = fields.String(required=False)
    text_type = fields.String(required=False)
    id = fields.Integer(required=False)
    is_deleted = fields.Boolean(required=False, default=False)

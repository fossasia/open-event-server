from marshmallow import Schema, fields


class TranslationSchema(Schema):
    """Translation Schema"""

    name = fields.String(required=True)
    language_code = fields.String(required=True)
    id = fields.Integer(required=False)
    isDeleted = fields.Boolean(required=False, default=False)

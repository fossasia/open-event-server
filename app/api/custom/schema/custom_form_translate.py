from marshmallow import Schema, fields


class TranslationSchema(Schema):
    name = fields.String(required=True)
    code = fields.String(required=True)
    id = fields.Integer(required=False)
    is_delete = fields.Boolean(required=False)
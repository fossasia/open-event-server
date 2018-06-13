from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema


class BaseSchema(Schema):
    deleted_at = fields.DateTime(allow_none=True)

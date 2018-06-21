from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema


class SoftDeletionSchema(Schema):
    """
        Base Schema for soft deletion support. All the schemas that support soft deletion should extend this schema
    """
    deleted_at = fields.DateTime(allow_none=True)

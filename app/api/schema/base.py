from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema


class SoftDeletionSchema(Schema):
    """
    Base Schema for soft deletion support. All the schemas that support soft deletion should extend this schema
    """

    deleted_at = fields.DateTime(allow_none=True)


class GetterRelationship(Relationship):
    """Use when relationship is not an attribute on the model, but a getter"""

    def __init__(self, *args, getter=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.getter = getter

    def serialize(self, attr, obj, accessor=None):
        return super().serialize(getattr(self, 'getter') or attr, obj, accessor)

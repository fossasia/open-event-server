from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class CustomSystemRoleSchema(Schema):
    """
    Api schema for Custom System Role Model
    """
    class Meta:
        """
        Meta class for Custom System Role Api Schema
        """
        type_ = 'custom-system-role'
        self_view = 'v1.custom_system_role_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)

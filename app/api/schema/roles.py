from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class RoleSchema(Schema):
    """
    Api schema for role Model
    """

    class Meta:
        """
        Meta class for role Api Schema
        """

        type_ = 'role'
        self_view = 'v1.role_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    title_name = fields.Str(allow_none=True)

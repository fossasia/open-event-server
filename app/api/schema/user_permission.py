from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.utilities import dasherize


class UserPermissionSchema(Schema):
    """
    Api schema for user permission Model
    """
    class Meta:
        """
        Meta class for user permission Api Schema
        """
        type_ = 'user-permission'
        self_view = 'v1.user_permission_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)

    unverified_user = fields.Boolean(allow_none=True)
    anonymous_user = fields.Boolean(allow_none=True)

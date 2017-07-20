from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.user_permission import UserPermission


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


class UserPermissionList(ResourceList):
    """
    List and create user permission
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = UserPermissionSchema
    data_layer = {'session': db.session,
                  'model': UserPermission}


class UserPermissionDetail(ResourceDetail):
    """
    User permission detail by id
    """
    schema = UserPermissionSchema
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session,
                  'model': UserPermission}

from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.bootstrap import api
from app.models.role import Role


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


class RoleList(ResourceList):
    """
    List and create role
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}


class RoleDetail(ResourceDetail):
    """
    Role detail by id
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role}

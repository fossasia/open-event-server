from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.api.bootstrap import api
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.api.helpers.db import safe_query


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
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('role_invite_id') is not None:
                role_invite = safe_query(self, RoleInvite, 'id', view_kwargs['role_invite_id'], 'role_invite_id')
                if role_invite.role_id is not None:
                    view_kwargs['id'] = role_invite.role_id
                else:
                    view_kwargs['id'] = None

        if view_kwargs.get('users_events_role_id') is not None:
                users_events_role = safe_query(self, UsersEventsRoles, 'id', view_kwargs['users_events_role_id'],
                'users_events_role_id')
                if users_events_role.role_id is not None:
                    view_kwargs['id'] = users_events_role.role_id
                else:
                    view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = RoleSchema
    data_layer = {'session': db.session,
                  'model': Role,
                  'methods': {
                      'before_get_object': before_get_object
                  }}

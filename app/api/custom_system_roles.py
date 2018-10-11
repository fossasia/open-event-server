from flask_rest_jsonapi import ResourceDetail, ResourceList, \
    ResourceRelationship

from app.api.bootstrap import api
from app.api.schema.custom_system_roles import CustomSystemRoleSchema
from app.models import db
from app.models.custom_system_role import CustomSysRole
from app.models.panel_permission import PanelPermission
from app.api.helpers.db import safe_query


class CustomSystemRoleList(ResourceList):
    """
    List and create Custom System Role
    """

    def query(self, view_kwargs):
        """
        query method for Panel Permission List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(CustomSysRole)
        if view_kwargs.get('panel_id'):
            panel = safe_query(self, PanelPermission, 'id', view_kwargs['panel_id'], 'panel_id')
            query_ = CustomSysRole.query.filter(CustomSysRole.panel_permissions.any(id=panel.id))

        return query_

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = CustomSystemRoleSchema
    data_layer = {'session': db.session,
                  'model': CustomSysRole,
                  'methods': {'query': query}}


class CustomSystemRoleDetail(ResourceDetail):
    """
    Custom System Role detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method for user object
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('role_id') is not None:
            panel_perm = safe_query(self, PanelPermission, 'id', view_kwargs['role_id'], 'role_id')
            if panel_perm.role_id is not None:
                view_kwargs['id'] = panel_perm.role_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomSystemRoleSchema
    data_layer = {'session': db.session,
                  'model': CustomSysRole}


class CustomSystemRoleRelationship(ResourceRelationship):
    """
    Custom System Role Relationship
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomSystemRoleSchema
    data_layer = {'session': db.session,
                  'model': CustomSysRole}

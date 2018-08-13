from flask_rest_jsonapi import ResourceDetail, ResourceList, \
    ResourceRelationship

from app.api.bootstrap import api
from app.api.schema.panel_permissions import PanelPermissionSchema
from app.models import db
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.models.panel_permission import PanelPermission
from app.models.custom_system_role import CustomSysRole


class PanelPermissionList(ResourceList):
    """
    List Panel Permission
    """

    def query(self, view_kwargs):
        """
        query method for Panel Permission List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(PanelPermission)
        if view_kwargs.get('custom_system_role_id'):
            role = safe_query(self, CustomSysRole, 'id', view_kwargs['custom_system_role_id'],
                              'custom_system_role_id')
            query_ = PanelPermission.query.filter(PanelPermission.custom_system_roles.any(id=role.id))

        return query_

    decorators = (api.has_permission('is_admin', methods="GET,POST"),)
    schema = PanelPermissionSchema
    data_layer = {'session': db.session,
                  'model': PanelPermission,
                  'methods': {'query': query}}


class PanelPermissionDetail(ResourceDetail):
    """
    Panel Permission detail by id
    """
    schema = PanelPermissionSchema
    decorators = (api.has_permission('is_admin', methods="GET,PATCH,DELETE"),)
    data_layer = {'session': db.session,
                  'model': PanelPermission}


class PanelPermissionRelationship(ResourceRelationship):
    """
    Panel Permission Relationship
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    methods = ['GET', 'PATCH']
    schema = PanelPermissionSchema
    data_layer = {'session': db.session,
                  'model': PanelPermission}

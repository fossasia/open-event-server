from flask_rest_jsonapi import ResourceDetail, ResourceList, \
    ResourceRelationship

from app.api.bootstrap import api
from app.api.schema.panel_permissions import PanelPermissionSchema
from app.models import db
from app.api.helpers.utilities import require_relationship
from app.models.panel_permission import PanelPermission


class PanelPermissionList(ResourceList):
    """
    List Panel Permission
    """
    @classmethod
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationships and permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['role'], data)

    decorators = (api.has_permission('is_admin', methods="GET,POST"),)
    schema = PanelPermissionSchema
    data_layer = {'session': db.session,
                  'model': PanelPermission}


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

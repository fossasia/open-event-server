from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.custom_system_roles import CustomSystemRoleSchema
from app.models import db
from app.models.custom_system_role import CustomSysRole


class CustomSystemRoleList(ResourceList):
    """
    List and create Custom System Role
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = CustomSystemRoleSchema
    data_layer = {'session': db.session,
                  'model': CustomSysRole}


class CustomSystemRoleDetail(ResourceDetail):
    """
    Custom System Role detail by id
    """

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomSystemRoleSchema
    data_layer = {'session': db.session,
                  'model': CustomSysRole}

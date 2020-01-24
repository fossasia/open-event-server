from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.schema.user_permission import UserPermissionSchema
from app.models import db
from app.models.user_permission import UserPermission


class UserPermissionList(ResourceList):
    """
    List and create user permission
    """

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = UserPermissionSchema
    data_layer = {'session': db.session, 'model': UserPermission}


class UserPermissionDetail(ResourceDetail):
    """
    User permission detail by id
    """

    schema = UserPermissionSchema
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    data_layer = {'session': db.session, 'model': UserPermission}

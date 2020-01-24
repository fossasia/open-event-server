from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.schema.event_role_permissions import EventsRolePermissionSchema
from app.models import db
from app.models.permission import Permission


class EventsRolePermissionList(ResourceList):
    """
    List Events Role Permission
    """

    decorators = (api.has_permission('is_admin', methods="GET"),)
    methods = ['GET']
    schema = EventsRolePermissionSchema
    data_layer = {'session': db.session, 'model': Permission}


class EventsRolePermissionDetail(ResourceDetail):
    """
    Events Role Permission detail by id
    """

    schema = EventsRolePermissionSchema
    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session, 'model': Permission}


class EventsRolePermissionRelationship(ResourceRelationship):
    """
    Events Role Permission Relationship
    """

    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = EventsRolePermissionSchema
    data_layer = {'session': db.session, 'model': Permission}

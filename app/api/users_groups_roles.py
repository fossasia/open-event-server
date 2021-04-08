from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.errors import ForbiddenError
from app.api.schema.users_groups_roles import UsersGroupsRolesSchema
from app.models import db
from app.models.users_groups_role import UsersGroupsRoles


class UsersGroupsRolesList(ResourceList):
    """
    List and create users_groups_roles
    """

    def query(self, view_kwargs):
        query_ = UsersGroupsRoles.query
        return query_

    view_kwargs = True
    decorators = (
        api.has_permission('is_coorganizer', fetch='group_id', model=UsersGroupsRoles),
    )
    methods = ['GET']
    schema = UsersGroupsRolesSchema
    data_layer = {
        'session': db.session,
        'model': UsersGroupsRoles,
        'methods': {'query': query},
    }


class UsersGroupsRolesDetail(ResourceDetail):
    """
    users_groups_roles detail by id
    """

    def before_delete_object(self, users_groups_roles, view_kwargs):
        role = users_groups_roles.role
        if role:
            if role.name == "owner":
                raise ForbiddenError(
                    {'source': 'Role'},
                    'You cannot remove the owner of the event.',
                )

    methods = ['GET', 'PATCH', 'DELETE']
    decorators = (
        api.has_permission('is_coorganizer', fetch='group_id', model=UsersGroupsRoles),
    )
    schema = UsersGroupsRolesSchema
    data_layer = {
        'session': db.session,
        'model': UsersGroupsRoles,
        'methods': {'before_delete_object': before_delete_object},
    }


class UsersGroupsRolesRelationship(ResourceRelationship):
    """
    users_groups_roles Relationship
    """

    methods = ['GET', 'PATCH']
    schema = UsersGroupsRolesSchema
    data_layer = {'session': db.session, 'model': UsersGroupsRoles}

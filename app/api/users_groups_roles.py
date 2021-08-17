from flask_jwt_extended import current_user
from flask_jwt_extended.view_decorators import jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.bootstrap import api
from app.api.helpers.errors import ConflictError, ForbiddenError
from app.api.helpers.utilities import require_relationship
from app.api.schema.users_groups_roles import UsersGroupsRolesSchema
from app.models import db
from app.models.group import Group
from app.models.role import Role
from app.models.user import User
from app.models.users_groups_role import UsersGroupsRoles


class UsersGroupsRolesList(ResourceList):
    """
    List and create users_groups_roles
    """

    def query(self, view_kwargs):
        query_ = UsersGroupsRoles.query
        if view_kwargs.get('group_id'):
            group = safe_query_kwargs(Group, view_kwargs, 'group_id')
            query_ = query_.filter_by(group_id=group.id)
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


class UsersGroupsRolesListPost(ResourceList):
    """
    Create users groups roles
    """

    def before_post(self, args, kwargs, data):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['group', 'role'], data)
        group = Group.query.get(data['group'])
        role = Role.query.get(data['role'])
        if group.user != current_user:
            raise ForbiddenError({'pointer': 'group'}, 'Owner access is required.')
        if role.name != 'organizer':
            raise ForbiddenError({'pointer': 'role'}, 'Only organizer role is allowed.')

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for UsersGroupsRolesListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        role_already_exists = UsersGroupsRoles.query.filter_by(
            email=data['email'], group_id=data['group'], role_id=data['role']
        ).count()
        if role_already_exists:
            raise ConflictError(
                {'source': '/data'}, 'Role Invite has already been sent for this email.'
            )
        user = User.query.filter_by(email=data['email']).first()
        if user:
            data['user_id'] = user.id

    def after_create_object(self, users_groups_role, data, view_kwargs):
        """
        after create object method for group_role_invite link
        :param role_invite:
        :param data:
        :param view_kwargs:
        :return:
        """
        users_groups_role.send_invite()

    view_kwargs = True
    decorators = (jwt_required,)
    methods = ['POST']
    schema = UsersGroupsRolesSchema
    data_layer = {
        'session': db.session,
        'model': UsersGroupsRoles,
        'methods': {
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
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

    methods = ['GET', 'DELETE']
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

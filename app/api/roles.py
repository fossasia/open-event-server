from flask_rest_jsonapi import ResourceDetail, ResourceList

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.roles import RoleSchema
from app.models import db
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from app.models.users_groups_role import UsersGroupsRoles


class RoleList(ResourceList):
    """
    List and create role
    """

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = RoleSchema
    data_layer = {'session': db.session, 'model': Role}


class RoleDetail(ResourceDetail):
    """
    Role detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('role_invite_id') is not None:
            role_invite = safe_query_kwargs(RoleInvite, view_kwargs, 'role_invite_id')
            view_kwargs['id'] = role_invite.role_id

        if view_kwargs.get('users_events_roles_id') is not None:
            users_events_role = safe_query_kwargs(
                UsersEventsRoles,
                view_kwargs,
                'users_events_roles_id',
            )
            view_kwargs['id'] = users_events_role.role_id

        if view_kwargs.get('users_groups_roles_id') is not None:
            users_groups_role = safe_query_kwargs(
                UsersGroupsRoles,
                view_kwargs,
                'users_groups_roles_id',
            )
            view_kwargs['id'] = users_groups_role.role_id

    def before_update_object(self, role, data, view_kwargs):
        """
        Method to edit object
        :param role:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('name'):
            if data['name'] in [
                'owner',
                'organizer',
                'coorganizer',
                'registrar',
                'moderator',
                'attendee',
                'track_organizer',
            ]:
                raise UnprocessableEntityError(
                    {'data': 'name'}, "The given name cannot be updated"
                )

    def before_delete_object(self, obj, kwargs):
        """
        method to check proper resource name before deleting
        :param obj:
        :param kwargs:
        :return:
        """
        if obj.name in [
            'owner',
            'organizer',
            'coorganizer',
            'registrar',
            'moderator',
            'attendee',
            'track_organizer',
        ]:
            raise UnprocessableEntityError(
                {'data': 'name'}, "The resource with given name cannot be deleted"
            )

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = RoleSchema
    data_layer = {
        'session': db.session,
        'model': Role,
        'methods': {
            'before_get_object': before_get_object,
            'before_delete_object': before_delete_object,
        },
    }

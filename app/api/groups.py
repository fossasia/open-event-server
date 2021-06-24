from flask import request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.schema.groups import GroupSchema

# models
from app.models import db
from app.models.event import Event
from app.models.group import Group
from app.models.user_follow_group import UserFollowGroup
from app.models.users_groups_role import UsersGroupsRoles


class GroupListPost(ResourceList):
    """
    Create and List Groups
    """

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for GroupListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        data['user_id'] = current_user.id
        if not current_user.is_verified:
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

        for event in data.get('events', []):
            if not has_access('is_owner', event_id=event):
                raise ForbiddenError({'source': ''}, "Event owner access required")

    schema = GroupSchema
    decorators = (jwt_required,)
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {
            'before_create_object': before_create_object,
        },
    }


class GroupList(ResourceList):
    def query(self, view_kwargs):
        """
        query method for GroupList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Group)

        if view_kwargs.get('user_id') and 'GET' in request.method:
            query_ = query_.filter_by(user_id=view_kwargs['user_id'])

        return query_

    view_kwargs = True
    decorators = (
        api.has_permission(
            'is_user_itself', methods="PATCH,DELETE", fetch="user_id", model=Group
        ),
    )
    schema = GroupSchema
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {'query': query},
    }


class GroupDetail(ResourceDetail):
    """
    GroupDetail class for GroupSchema
    """

    def before_get_object(self, view_kwargs):

        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            view_kwargs['id'] = event.group_id

        if view_kwargs.get('users_groups_roles_id') is not None:
            users_groups_role = safe_query_kwargs(
                UsersGroupsRoles,
                view_kwargs,
                'users_groups_roles_id',
            )
            view_kwargs['id'] = users_groups_role.role_id

        if view_kwargs.get('user_follow_group_id') is not None:
            user_follow_group = safe_query_kwargs(
                UserFollowGroup,
                view_kwargs,
                'user_follow_group_id',
            )
            view_kwargs['id'] = user_follow_group.group_id

    def before_update_object(self, group, data, view_kwargs):
        """
        before update object method of group details
        :param group:
        :param data:
        :param view_kwargs:
        :return:
        """

        for event in data.get('events', []):
            if not has_access('is_owner', event_id=event):
                raise ForbiddenError({'source': ''}, "Event owner access required")

    decorators = (
        api.has_permission(
            'is_user_itself', methods="PATCH,DELETE", fetch="user_id", model=Group
        ),
    )
    schema = GroupSchema
    methods = ["GET", "PATCH", "DELETE"]
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
        },
    }


class GroupRelationship(ResourceRelationship):
    """
    Group Relationship
    """

    decorators = (
        api.has_permission(
            'is_user_itself', methods="PATCH", fetch="user_id", model=Group
        ),
    )
    methods = ["GET", "PATCH"]
    schema = GroupSchema
    data_layer = {
        'session': db.session,
        'model': Group,
    }

from flask import request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.permissions import jwt_required
from app.api.schema.groups import GroupSchema

# models
from app.models import db
from app.models.event import Event
from app.models.group import Group
from app.models.role import Role
from app.models.user import User
from app.models.user_follow_group import UserFollowGroup
from app.models.users_groups_role import UsersGroupsRoles


def is_owner_or_organizer(group, user):
    """
    Checks if the user is admin, owner or organizer of group
    """
    is_admin = user.is_staff
    is_owner = group.user == user
    is_organizer = False
    organizer_role = Role.query.filter_by(name='organizer').first()
    if organizer_role:
        is_organizer = bool(
            UsersGroupsRoles.query.filter_by(
                group_id=group.id, role_id=organizer_role.id, accepted=True
            ).all()
        )
    return is_admin or is_owner or is_organizer


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

    def after_create_object(self, group, data, view_kwargs):
        if data.get('banner_url'):
            start_image_resizing_tasks(group, data['banner_url'])

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
            'after_create_object': after_create_object,
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

        user = User.query.filter_by(id=current_user.id).one()
        if not is_logged_in() or not is_owner_or_organizer(group, user):
            raise ForbiddenError(
                {'source': 'user_id'}, "Group owner or organizer access required"
            )

        for event in data.get('events', []):
            if not has_access('is_owner', event_id=event):
                raise ForbiddenError({'source': ''}, "Event owner access required")

        if data.get('banner_url'):
            start_image_resizing_tasks(group, data['banner_url'])

    decorators = (jwt_required,)
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


def start_image_resizing_tasks(group, banner_url):
    group_id = str(group.id)
    from .helpers.tasks import resize_group_images_task

    resize_group_images_task.delay(group_id, banner_url)

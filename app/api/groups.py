from flask import request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.schema.groups import GroupSchema

# models
from app.models import db
from app.models.group import Group
from app.models.user import User


class GroupListPost(ResourceList):
    """
    Create and List Groups
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for required relationship with group
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        data['user'] = current_user.id
        user = User.query.get(data['user'])
        if not user.is_verified:
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

    schema = GroupSchema
    decorators = (jwt_required,)
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {'before_post': before_post},
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
            if not has_access('is_user_itself', user_id=view_kwargs['user_id']):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.filter_by(user_id=user.id)

        return query_

    view_kwargs = True
    decorators = (jwt_required,)
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
        """
        before get object method for group detail
        :param view_kwargs:
        :return:
        """
        group = safe_query_kwargs(Group, view_kwargs, 'id')
        if not has_access(
            'is_user_itself',
            user_id=group.user_id,
        ):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    def before_delete_object(self, obj, kwargs):
        """
        before delete object method for group detail
        :param obj:
        :param kwargs:
        :return:
        """
        group = safe_query_kwargs(Group, view_kwargs, 'id')
        if not has_access(
            'is_user_itself',
            user_id=group.user_id,
        ):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    def before_update_object(self, obj, data, kwargs):
        """
        before update object method for group detail
        :param obj:
        :param data:
        :param kwargs:
        :return:
        """
        group = safe_query_kwargs(Group, view_kwargs, 'id')
        if not has_access(
            'is_user_itself',
            user_id=group.user_id,
        ):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    decorators = (jwt_required,)
    schema = GroupSchema
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {
            'before_update_object': before_update_object,
            'before_get_object': before_get_object,
            'before_delete_object': before_delete_object,
        },
    }


class GroupRelationship(ResourceRelationship):
    """
    Group Relationship
    """

    def before_get_object(self, view_kwargs):
        """
        before get object method for group relationship
        :param view_kwargs:
        :return:
        """
        group = safe_query_kwargs(Group, view_kwargs, 'id')
        if not has_access(
            'is_user_itself',
            user_id=group.user_id,
        ):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    decorators = (jwt_required,)
    schema = GroupSchema
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {'before_get_object': before_get_object},
    }

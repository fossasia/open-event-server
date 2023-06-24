from flask_jwt_extended import current_user, jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.permission_manager import is_logged_in
from app.api.helpers.utilities import require_relationship
from app.api.schema.user_follow_groups import UserFollowGroupSchema
from app.models import db
from app.models.group import Group
from app.models.user import User
from app.models.user_follow_group import UserFollowGroup


class UserFollowGroupListPost(ResourceList):
    """
    Create User Follow Group
    """

    @classmethod
    def before_post(cls, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['group'], data)

        data['user'] = current_user.id
        user_follow_group = UserFollowGroup.query.filter_by(
            group_id=data['group'], user=current_user
        ).first()
        if user_follow_group:
            raise ConflictError(
                {'pointer': '/data/relationships/group'}, "Group already followed"
            )

    view_kwargs = True
    decorators = (jwt_required,)
    schema = UserFollowGroupSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': UserFollowGroup,
        'methods': {'before_post': before_post},
    }


class UserFollowGroupList(ResourceList):
    """
    List User Followed Groups
    """

    def query(self, view_kwargs):
        query_ = UserFollowGroup.query

        if view_kwargs.get('user_id') is not None:
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if user != current_user or not is_logged_in():
                raise ForbiddenError({'pointer': 'user_id'})
            query_ = query_.filter_by(user_id=user.id)

        elif view_kwargs.get('group_id') is not None:
            group = safe_query_kwargs(Group, view_kwargs, 'group_id')
            query_ = query_.filter_by(group_id=group.id)

        return query_

    view_kwargs = True
    methods = ['GET']
    decorators = (jwt_required,)
    schema = UserFollowGroupSchema
    data_layer = {
        'session': db.session,
        'model': UserFollowGroup,
        'methods': {'query': query},
    }


class UserFollowGroupDetail(ResourceDetail):
    """
    User followed group detail by id
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            view_kwargs['id'] = user.id

    def after_get_object(self, follower, view_kwargs):
        if not follower:
            raise NotFoundError({'source': ''}, 'Group Not Found')

    def before_delete_object(self, follower, view_kwargs):
        if not follower:
            raise NotFoundError({'source': ''}, 'Group Follower Not Found')
        if current_user.id != follower.user_id:
            raise ForbiddenError(
                {'source': ''}, 'User have no permission to delete follower'
            )

    view_kwargs = True
    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = UserFollowGroupSchema
    data_layer = {
        'session': db.session,
        'model': UserFollowGroup,
        'methods': {
            'after_get_object': after_get_object,
            'before_delete_object': before_delete_object,
        },
    }


class UserFollowGroupRelationship(ResourceRelationship):
    """
    User Followed Group Relationship
    """

    schema = UserFollowGroupSchema
    decorators = (jwt_required,)
    methods = ['GET']
    data_layer = {'session': db.session, 'model': UserFollowGroup}

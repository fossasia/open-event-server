from flask_jwt_extended import current_user, jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError, NotFoundError
from app.api.helpers.permission_manager import is_logged_in
from app.api.helpers.utilities import require_relationship
from app.api.schema.group_followers import GroupFollowerSchema
from app.models import db
from app.models.group import Group
from app.models.group_follower import GroupFollower
from app.models.user import User


class GroupFollowerListPost(ResourceList):
    """
    Create Group Follower
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
        group_followed_user = GroupFollower.query.filter_by(
            group_id=data['group'], user=current_user
        ).first()
        if group_followed_user:
            raise ConflictError(
                {'pointer': '/data/relationships/group'}, "Group already followed"
            )

    view_kwargs = True
    decorators = (jwt_required,)
    schema = GroupFollowerSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': GroupFollower,
        'methods': {'before_post': before_post},
    }


class UserGroupFollowedList(ResourceList):
    """
    List User Followed Groups
    """

    def query(self, view_kwargs):
        query_ = GroupFollower.query
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if user != current_user or not is_logged_in():
                raise ForbiddenError({'pointer': 'user_id'})
            query_ = query_.filter_by(user_id=user.id)

        elif view_kwargs.get('group_id'):
            group = safe_query_kwargs(Group, view_kwargs, 'group_id')
            query_ = query_.filter_by(group_id=group.id)

        return query_

    methods = ['GET']
    schema = GroupFollowerSchema
    data_layer = {
        'session': db.session,
        'model': GroupFollower,
        'methods': {'query': query},
    }


class UserGroupFollowedDetail(ResourceDetail):
    """
    User followed group detail by id
    """

    def after_get_object(self, follower, view_kwargs):
        if not follower:
            raise NotFoundError({'source': ''}, 'Group Not Found')

    def before_delete_object(self, follower, view_kwargs):
        if not follower:
            raise NotFoundError({'source': ''}, 'Group Not Found')

    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = GroupFollowerSchema
    data_layer = {
        'session': db.session,
        'model': GroupFollower,
        'methods': {
            'after_get_object': after_get_object,
            'before_delete_object': before_delete_object,
        },
    }


class UserGroupFollowedRelationship(ResourceRelationship):
    """
    User Followed Group Relationship
    """

    schema = GroupFollowerSchema
    decorators = (jwt_required,)
    methods = ['GET']
    data_layer = {'session': db.session, 'model': GroupFollower}

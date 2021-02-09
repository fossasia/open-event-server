from flask_jwt_extended import current_user, jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import require_relationship
from app.api.schema.user_favourite_sessions import UserFavouriteSessionSchema
from app.models import db
from app.models.event import Event
from app.models.session import Session
from app.models.user import User
from app.models.user_favourite_session import UserFavouriteSession


class UserFavouriteSessionListPost(ResourceList):
    """
    Create User Favourite Session
    """

    @classmethod
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['session'], data)

        data['user'] = current_user.id
        user_favourite_session = find_user_favourite_session_by_id(
            session_id=data['session']
        )
        if user_favourite_session:
            raise ConflictError(
                {'pointer': '/data/relationships/session'}, "Session already favourited"
            )

    view_kwargs = True
    decorators = (jwt_required,)
    schema = UserFavouriteSessionSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': UserFavouriteSession,
        'methods': {'before_post': before_post},
    }


class UserFavouriteSessionList(ResourceList):
    """
    List User Favourite Sessions
    """

    def query(self, view_kwargs):
        query_ = UserFavouriteSession.query
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if user != current_user and not has_access('is_admin'):
                raise ForbiddenError({'pointer': 'user_id'})
            query_ = query_.filter_by(user_id=user.id)

        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            if not (
                has_access('is_admin') or has_access('is_coorganizer', session.event_id)
            ):
                query_ = query_.filter_by(user_id=current_user.id)
            query_ = query_.filter_by(session_id=session.id)

        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            if not (has_access('is_admin') or has_access('is_coorganizer', event.id)):
                query_ = query_.filter_by(user_id=current_user.id)
            query_ = query_.filter_by(event_id=event.id)

        return query_

    methods = ['GET']
    decorators = (jwt_required,)
    schema = UserFavouriteSessionSchema
    data_layer = {
        'session': db.session,
        'model': UserFavouriteSession,
        'methods': {'query': query},
    }


class UserFavouriteSessionDetail(ResourceDetail):
    """
    User Favourite Session detail by id
    """

    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = UserFavouriteSessionSchema
    data_layer = {'session': db.session, 'model': UserFavouriteSession}


class UserFavouriteSessionRelationship(ResourceRelationship):
    """
    User Favourite Session Relationship
    """

    schema = UserFavouriteSessionSchema
    decorators = (jwt_required,)
    methods = ['GET']
    data_layer = {'session': db.session, 'model': UserFavouriteSession}


def find_user_favourite_session_by_id(session_id):
    return UserFavouriteSession.query.filter_by(
        session_id=session_id, user=current_user
    ).first()

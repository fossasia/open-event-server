from flask_jwt_extended import current_user, jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ConflictError
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
        """
        query method for SessionList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(UserFavouriteSession)
        if view_kwargs.get('user_id') is not None:
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        elif has_access('is_admin'):
            pass

        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            if not has_access('is_admin'):
                query_ = query_.join(User).filter(User.id == current_user.id)
            query_ = query_.join(Session).filter(Session.id == session.id)

        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            if not has_access('is_admin'):
                # if not(request.json['data']['all'] and has_access('is_coorganizer')):
                query_ = query_.join(User).filter(User.id == current_user.id)
            query_ = query_.join(Session.event).filter(Event.id == event.id)

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

    def before_get_object(self, view_kwargs):

        if view_kwargs.get('id') is not None:
            try:
                user_favourite_session = find_user_favourite_session_by_id(
                    session_id=view_kwargs['id']
                )
            except NoResultFound:
                raise ObjectNotFound(
                    {'source': '/data/relationships/session'}, "Object: not found"
                )
            else:
                if user_favourite_session is not None:
                    view_kwargs['id'] = user_favourite_session.id
                else:
                    view_kwargs['id'] = None

    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = UserFavouriteSessionSchema
    data_layer = {
        'session': db.session,
        'model': UserFavouriteSession,
        'methods': {
            'before_get_object': before_get_object,
        },
    }


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

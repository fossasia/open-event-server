from flask_jwt_extended import current_user, jwt_required, verify_jwt_in_request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.utilities import require_relationship
from app.api.schema.user_favourite_events import UserFavouriteEventSchema
from app.models import db
from app.models.user import User
from app.models.user_favourite_event import UserFavouriteEvent


class UserFavouriteEventListPost(ResourceList):
    """
    Create User Favourite Events
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
        require_relationship(['event'], data)

        if is_logged_in():
            verify_jwt_in_request()
        else:
            raise ForbiddenError(
                {'source': ''}, 'Only Authorized Users can favourite an event'
            )

        data['user'] = current_user.id
        user_favourite_event = find_user_favourite_event_by_id(event_id=data['event'])
        if user_favourite_event:
            raise ConflictError(
                {'pointer': '/data/relationships/event'}, "Event already favourited"
            )

    view_kwargs = True
    schema = UserFavouriteEventSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': UserFavouriteEvent,
        'methods': {'before_post': before_post},
    }


class UserFavouriteEventList(ResourceList):
    """
    List User Favourite Events
    """

    def query(self, view_kwargs):
        """
        query method for SessionList class
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(UserFavouriteEvent)
        if view_kwargs.get('user_id') is not None:
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        elif has_access('is_admin'):
            pass

        return query_

    methods = ['GET']
    schema = UserFavouriteEventSchema
    data_layer = {
        'session': db.session,
        'model': UserFavouriteEvent,
        'methods': {'query': query},
    }


class UserFavouriteEventDetail(ResourceDetail):
    """
    User Favourite Events detail by id
    """

    @jwt_required
    def before_get_object(self, view_kwargs):

        if view_kwargs.get('id') is not None:
            try:
                user_favourite_event = find_user_favourite_event_by_id(
                    event_id=view_kwargs['id']
                )
            except NoResultFound:
                raise ObjectNotFound(
                    {'source': '/data/relationships/event'}, "Object: not found"
                )
            else:
                if user_favourite_event is not None:
                    view_kwargs['id'] = user_favourite_event.id
                else:
                    view_kwargs['id'] = None

    methods = ['GET', 'DELETE']
    schema = UserFavouriteEventSchema
    data_layer = {
        'session': db.session,
        'model': UserFavouriteEvent,
        'methods': {
            'before_get_object': before_get_object,
        },
    }


class UserFavouriteEventRelationship(ResourceRelationship):
    """
    User Favourite Events Relationship
    """

    schema = UserFavouriteEventSchema
    methods = ['GET']
    data_layer = {'session': db.session, 'model': UserFavouriteEvent}


def find_user_favourite_event_by_id(event_id):
    return UserFavouriteEvent.query.filter_by(
        deleted_at=None, user=current_user, event_id=event_id
    ).first()

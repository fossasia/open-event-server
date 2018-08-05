from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask import request, current_app as app
from flask_jwt import current_identity as current_user, _jwt_required

from app.models.user import User
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.exceptions import ForbiddenException, ConflictException
from app.api.helpers.utilities import require_relationship
from app.api.schema.user_favourite_events import UserFavouriteEventSchema
from app.models import db
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

        if 'Authorization' in request.headers:
            _jwt_required(app.config['JWT_DEFAULT_REALM'])
        else:
            raise ForbiddenException({'source': ''}, 'Only Authorized Users can favourite an event')

        data['user'] = current_user.id
        user_favourite_event = UserFavouriteEvent.query.filter_by(
                                   user=current_user, event_id=int(data['event'])).first()
        if user_favourite_event:
            raise ConflictException({'pointer': '/data/relationships/event'}, "Event already favourited")

    view_kwargs = True
    schema = UserFavouriteEventSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': UserFavouriteEvent,
                  'methods': {'before_post': before_post}}


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
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        elif has_access('is_admin'):
            pass

        return query_

    methods = ['GET']
    schema = UserFavouriteEventSchema
    data_layer = {'session': db.session,
                  'model': UserFavouriteEvent,
                  'methods': {
                      'query': query
                  }}


class UserFavouriteEventDetail(ResourceDetail):
    """
    User Favourite Events detail by id
    """

    methods = ['GET', 'DELETE']
    schema = UserFavouriteEventSchema
    data_layer = {'session': db.session,
                  'model': UserFavouriteEvent}


class UserFavouriteEventRelationship(ResourceRelationship):
    """
    User Favourite Events Relationship
    """
    schema = UserFavouriteEventSchema
    methods = ['GET']
    data_layer = {'session': db.session,
                  'model': UserFavouriteEvent}

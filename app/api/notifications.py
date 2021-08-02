from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.schema.notifications import NotificationSchema
from app.models import db
from app.models.notification import Notification
from app.models.user import User


class NotificationListAdmin(ResourceList):
    """
    List all the Notification
    """

    decorators = (api.has_permission('is_admin'),)
    methods = ['GET']
    schema = NotificationSchema
    data_layer = {'session': db.session, 'model': Notification}


class NotificationList(ResourceList):
    """
    List all the Notification
    """

    def query(self, view_kwargs):
        """
        query method for Notifications list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Notification)
        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('user_id') is not None:
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            data['user_id'] = user.id

    view_kwargs = True
    decorators = (
        api.has_permission('is_user_itself', fetch="user_id", model=Notification),
    )
    methods = ['GET']
    schema = NotificationSchema
    data_layer = {
        'session': db.session,
        'model': Notification,
        'methods': {'query': query, 'before_create_object': before_create_object},
    }


class NotificationDetail(ResourceDetail):
    """
    Notification detail by ID
    """

    decorators = (
        api.has_permission(
            'is_user_itself', methods="PATCH,DELETE", fetch="user_id", model=Notification
        ),
    )
    schema = NotificationSchema
    data_layer = {
        'session': db.session,
        'model': Notification,
    }


class NotificationRelationship(ResourceRelationship):
    """
    Notification Relationship
    """

    decorators = (
        api.has_permission('is_user_itself', fetch="user_id", model=Notification),
    )
    schema = NotificationSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session, 'model': Notification}

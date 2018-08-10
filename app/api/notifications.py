from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.notifications import NotificationSchema, NotificationActionSchema
from app.models import db
from app.models.notification import Notification, NotificationAction
from app.models.user import User


class NotificationListAdmin(ResourceList):
    """
    List all the Notification
    """
    decorators = (api.has_permission('is_admin'),)
    methods = ['GET']
    schema = NotificationSchema
    data_layer = {'session': db.session,
                  'model': Notification}


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
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
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
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            data['user_id'] = user.id

    view_kwargs = True
    decorators = (api.has_permission('is_user_itself', fetch="user_id", model=Notification),)
    methods = ['GET']
    schema = NotificationSchema
    data_layer = {'session': db.session,
                  'model': Notification,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class NotificationDetail(ResourceDetail):
    """
    Notification detail by ID
    """
    def before_get(self, args, kwargs):
        if kwargs.get('notification_action_id'):
            notification_action = safe_query(db, NotificationAction,
                                             'id', kwargs['notification_action_id'], 'notification_action_id')
            kwargs['id'] = notification_action.notification_id

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('notification_action_id'):
            notification_action = safe_query(self, NotificationAction,
                                             'id', view_kwargs['notification_action_id'], 'notification_action_id')
            view_kwargs['id'] = notification_action.notification_id

    decorators = (api.has_permission('is_user_itself', methods="PATCH,DELETE", fetch="user_id", model=Notification),)
    schema = NotificationSchema
    data_layer = {'session': db.session,
                  'model': Notification,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class NotificationRelationship(ResourceRelationship):
    """
    Notification Relationship
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", model=Notification),)
    schema = NotificationSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': Notification}


class NotificationActionList(ResourceList):
    """
    List all the Notification-actions
    """
    decorators = (api.has_permission('is_admin'),)
    methods = ['GET']
    schema = NotificationSchema
    data_layer = {'session': db.session,
                  'model': Notification}


class NotificationActionDetail(ResourceDetail):
    """
    Notification action detail by ID
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", model=Notification),)
    schema = NotificationActionSchema
    data_layer = {'session': db.session,
                  'model': NotificationAction}


class NotificationActionRelationship(ResourceRelationship):
    """
    Notification Relationship
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", model=Notification),)
    schema = NotificationActionSchema
    methods = ['GET', 'PATCH']
    data_layer = {'session': db.session,
                  'model': NotificationAction}

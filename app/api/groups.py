from flask import request
from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.groups import GroupSchema

# models
from app.models import db
from app.models.event import Event
from app.models.group import Group


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
        require_relationship(['event'], data)
        if not current_user.is_verified:
            raise ForbiddenError({'source': ''}, 'Access Forbidden')

    def after_create_object(self, group, data, view_kwargs):
        if 'events' in data:
            for event_id in data['events']:
                event = safe_query(Event, 'id', event_id, 'event_id')
                event.group_id = group.id

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
            if event.group_id:
                view_kwargs['id'] = event.group_id
            else:
                view_kwargs['id'] = None

    decorators = (
        api.has_permission(
            'is_user_itself', methods="PATCH,DELETE", fetch="user_id", model=Group
        ),
    )
    schema = GroupSchema
    methods = ["GET", "PATCH", "DELETE"]
    data_layer = {
        'session': db.session,
        'model': Group,
        'methods': {
            'before_get_object': before_get_object,
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

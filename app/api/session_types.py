from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.session_types import SessionTypeSchema
from app.models import db
from app.models.session import Session
from app.models.session_type import SessionType


class SessionTypeListPost(ResourceList):
    """
    List and create sessions
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

        if not has_access('is_coorganizer', event_id=data['event']):
            raise ForbiddenException({'source': ''}, 'Co-organizer access is required.')

    methods = ['POST', ]
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType}


class SessionTypeList(ResourceList):
    """
    List sessions
    """
    def query(self, view_kwargs):
        """
        query method for Session Type List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(SessionType)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    methods = ['GET', ]
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType,
                  'methods': {
                      'query': query,
                  }}


class SessionTypeDetail(ResourceDetail):
    """
    Detail about a single session type by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method for session type detail
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('session_id'):
            session = safe_query(self, Session, 'id', view_kwargs['session_id'], 'session_id')
            if session.session_type_id:
                view_kwargs['id'] = session.session_type_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=SessionType),)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class SessionTypeRelationshipRequired(ResourceRelationship):
    """
    SessionType Relationship
    """
    methods = ['GET', 'PATCH']
    decorators = (api.has_permission('is_coorganizer', methods="PATCH", fetch="event_id", fetch_as="event_id",
                                     model=SessionType),)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType}


class SessionTypeRelationshipOptional(ResourceRelationship):
    """
    SessionType Relationship
    """
    decorators = (api.has_permission('is_coorganizer', methods="PATCH,DELETE", fetch="event_id", fetch_as="event_id",
                                     model=SessionType),)
    schema = SessionTypeSchema
    data_layer = {'session': db.session,
                  'model': SessionType}

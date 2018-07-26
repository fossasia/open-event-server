from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.feedbacks import FeedbackSchema
from app.models import db
from app.models.feedback import Feedback
from app.models.event import Event


class FeedbackListPost(ResourceList):
    """
    Create and List Feedbacks
    """

    def before_post(self, args, kwargs, data):
        """
        method to check for required relationship with event
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['user'], data)
        if not has_access('is_user_itself', user_id=int(data['user'])):
            raise ObjectNotFound({'parameter': 'user_id'},
                                 "User: {} doesn't match auth key".format(data['user']))
        if 'event' in data and 'session' in data:
            raise UnprocessableEntity({'pointer': ''},
                                      "Only one relationship between event and session is allowed")
        if 'event' not in data and 'session' not in data:
            raise UnprocessableEntity({'pointer': ''},
                                      "A valid relationship with event and session is required")

    schema = FeedbackSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Feedback
                  }


class FeedbackList(ResourceList):
    """
    Show List of Feedback
    """

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(Feedback)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    decorators = (jwt_required,)
    methods = ['GET', ]
    schema = FeedbackSchema
    data_layer = {'session': db.session,
                  'model': Feedback,
                  'methods': {
                      'query': query
                  }}


class FeedbackDetail(ResourceDetail):
    """
    Feedback Resource
    """

    def before_get_object(self, view_kwargs):
        """
        before get method
        :param view_kwargs:
        :return:
        """
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')

        if event:
            feedback = safe_query(self, Feedback, 'event_id', event.id, 'event_id')
            view_kwargs['id'] = feedback.id

    decorators = (api.has_permission('is_user_itself', fetch='user_id',
                                     fetch_as="user_id", model=Feedback, methods="PATCH,DELETE"),)
    schema = FeedbackSchema
    data_layer = {'session': db.session,
                  'model': Feedback}


class FeedbackRelationship(ResourceRelationship):
    """
    Feedback Relationship
    """
    decorators = (api.has_permission('is_user_itself', fetch='user_id',
                                     fetch_as="user_id", model=Feedback, methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = FeedbackSchema
    data_layer = {'session': db.session,
                  'model': Feedback}

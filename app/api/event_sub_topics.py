from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.custom_placeholders import CustomPlaceholder
from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.utilities import require_relationship
from app.api.schema.event_sub_topics import EventSubTopicSchema
from app.models import db
from app.models.event import Event
from app.models.event_sub_topic import EventSubTopic
from app.models.event_topic import EventTopic


class EventSubTopicListPost(ResourceList):
    """
    Create event sub topics
    """

    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event_topic'], data)
        if not has_access('is_admin'):
            raise ForbiddenError({'source': ''}, 'Admin access is required.')

    view_kwargs = True
    methods = [
        'POST',
    ]
    schema = EventSubTopicSchema
    data_layer = {'session': db.session, 'model': EventSubTopic}


class EventSubTopicList(ResourceList):
    """
    List event sub topics
    """

    def query(self, view_kwargs):
        """
        query method for event sub-topics list
        :param view_kwargs:
        :return:
        """

        query_ = self.session.query(EventSubTopic)
        if view_kwargs.get('event_topic_id'):
            event_topic = safe_query_kwargs(EventTopic, view_kwargs, 'event_topic_id')
            query_ = query_.join(EventTopic).filter(EventTopic.id == event_topic.id)
        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    schema = EventSubTopicSchema
    data_layer = {
        'session': db.session,
        'model': EventSubTopic,
        'methods': {'query': query},
    }


class EventSubTopicDetail(ResourceDetail):
    """
    Event sub topic detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id to fetch details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query_kwargs(
                Event, view_kwargs, 'event_identifier', 'identifier'
            )
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            if event.event_sub_topic_id:
                view_kwargs['id'] = event.event_sub_topic_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('custom_placeholder_id'):
            custom_placeholder = safe_query_kwargs(
                CustomPlaceholder,
                view_kwargs,
                'custom_placeholder_id',
            )
            if custom_placeholder.event_sub_topic_id:
                view_kwargs['id'] = custom_placeholder.event_sub_topic_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventSubTopicSchema
    data_layer = {
        'session': db.session,
        'model': EventSubTopic,
        'methods': {'before_get_object': before_get_object},
    }


class EventSubTopicRelationshipRequired(ResourceRelationship):
    """
    Event sub topic Relationship
    """

    decorators = (api.has_permission('is_admin', methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = EventSubTopicSchema
    data_layer = {'session': db.session, 'model': EventSubTopic}


class EventSubTopicRelationshipOptional(ResourceRelationship):
    """
    Event sub topic Relationship
    """

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventSubTopicSchema
    data_layer = {'session': db.session, 'model': EventSubTopic}

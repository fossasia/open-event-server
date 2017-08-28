from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.event_topics import EventTopicSchema
from app.models import db
from app.models.event import Event
from app.models.event_sub_topic import EventSubTopic
from app.models.event_topic import EventTopic


class EventTopicList(ResourceList):

    """
    List and create event topics
    """
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic}


class EventTopicDetail(ResourceDetail):
    """
    Event topic detail by id
    """
    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            if event.event_topic_id:
                view_kwargs['id'] = event.event_topic_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query(self, EventSubTopic, 'id', view_kwargs['event_sub_topic_id'],
                                         'event_sub_topic_id')
            if event_sub_topic.event_topic_id:
                view_kwargs['id'] = event_sub_topic.event_topic_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventTopicRelationship(ResourceRelationship):
    """
    Event topic Relationship
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic}

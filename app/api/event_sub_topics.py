from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event_sub_topic import EventSubTopic
from app.models.event import Event
from app.models.event_topic import EventTopic
from app.api.bootstrap import api
from app.api.helpers.permissions import jwt_required
from app.api.helpers.db import safe_query
from app.api.custom_placeholders import CustomPlaceholder


class EventSubTopicSchema(Schema):
    """
    Api Schema for event sub topic model
    """

    class Meta:
        """
        Meta class for event sub topic Api Schema
        """
        type_ = 'event-sub-topic'
        self_view = 'v1.event_sub_topic_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(dump_only=True)
    events = Relationship(attribute='event',
                          self_view='v1.event_topic_event',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.event_list',
                          related_view_kwargs={'event_sub_topic_id': '<id>'},
                          schema='EventSchema',
                          type_='event')
    event_topic = Relationship(attribute='event_topic',
                               self_view='v1.event_sub_topic_event_topic',
                               self_view_kwargs={'id': '<id>'},
                               related_view='v1.event_topic_detail',
                               related_view_kwargs={'event_sub_topic_id': '<id>'},
                               schema='EventTopicSchema',
                               type_='event-topic')
    custom_placeholder = Relationship(attribute='custom_placeholder',
                                      self_view='v1.event_sub_topic_custom_placeholder',
                                      self_view_kwargs={'id': '<id>'},
                                      related_view='v1.custom_placeholder_detail',
                                      related_view_kwargs={'event_sub_topic_id': '<id>'},
                                      schema='CustomPlaceholderSchema',
                                      type_='custom-placeholder')


class EventSubTopicList(ResourceList):
    """
    List and create event sub topics
    """

    def query(self, view_kwargs):
        """
        query method for event sub-topics list
        :param view_kwargs:
        :return:
        """

        query_ = self.session.query(EventSubTopic)
        if view_kwargs.get('event_topic_id'):
            event_topic = safe_query(self, EventTopic, 'id', view_kwargs['event_topic_id'], 'event_topic_id')
            query_ = query_.join(EventTopic).filter(EventTopic.id == event_topic.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_topic_id'):
            event_topic = safe_query(self, EventTopic, 'id', view_kwargs['event_topic_id'], 'event_topic_id')
            data['event_topic_id'] = event_topic.id

    view_kwargs = True
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventSubTopicSchema
    data_layer = {'session': db.session,
                  'model': EventSubTopic,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class EventSubTopicDetail(ResourceDetail):
    """
    Event sub topic detail by id
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            if event.event_sub_topic_id:
                view_kwargs['id'] = event.event_sub_topic_id
            else:
                view_kwargs['id'] = None

        if view_kwargs.get('custom_placeholder_id'):
            custom_placeholder = safe_query(self, CustomPlaceholder, 'id', view_kwargs['custom_placeholder_id'],
                                            'custom_placeholder_id')
            if custom_placeholder.event_sub_topic_id:
                view_kwargs['id'] = custom_placeholder.event_sub_topic_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventSubTopicSchema
    data_layer = {'session': db.session,
                  'model': EventSubTopic,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventSubTopicRelationship(ResourceRelationship):
    """
    Event sub topic Relationship
    """
    decorators = (jwt_required,)
    schema = EventSubTopicSchema
    data_layer = {'session': db.session,
                  'model': EventSubTopic}

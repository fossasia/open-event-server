from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event_topic import EventTopic
from app.models.event_sub_topic import EventSubTopic
from app.models.event import Event
from app.api.bootstrap import api
from app.api.helpers.permissions import jwt_required
from app.api.helpers.db import safe_query


class EventTopicSchema(Schema):
    """
    Api Schema for event topic model
    """

    class Meta:
        """
        Meta class for event topic Api Schema
        """
        type_ = 'event-topic'
        self_view = 'v1.event_topic_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    slug = fields.Str(dump_only=True)
    events = Relationship(attribute='event',
                          self_view='v1.event_topic_event',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.event_list',
                          related_view_kwargs={'event_topic_id': '<id>'},
                          schema='EventSchema',
                          type_='event')
    event_sub_topics = Relationship(attribute='event_sub_topics',
                                    self_view='v1.event_topic_event_sub_topic',
                                    self_view_kwargs={'id': '<id>'},
                                    related_view='v1.event_sub_topic_list',
                                    related_view_kwargs={'event_topic_id': '<id>'},
                                    many=True,
                                    schema='EventSubTopicSchema',
                                    type_='event-sub-topic')


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
    decorators = (jwt_required, )
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic}

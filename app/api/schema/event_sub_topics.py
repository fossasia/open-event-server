from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


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
    events = Relationship(
        attribute='event',
        many=True,
        self_view='v1.event_topic_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        related_view_kwargs={'event_sub_topic_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    event_topic = Relationship(
        self_view='v1.event_sub_topic_event_topic',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_topic_detail',
        related_view_kwargs={'event_sub_topic_id': '<id>'},
        schema='EventTopicSchema',
        type_='event-topic',
    )
    custom_placeholder = Relationship(
        self_view='v1.event_sub_topic_custom_placeholder',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.custom_placeholder_detail',
        related_view_kwargs={'event_sub_topic_id': '<id>'},
        schema='CustomPlaceholderSchema',
        type_='custom-placeholder',
    )

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class EventTopicSchema(SoftDeletionSchema):
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
    system_image_url = fields.Url()
    slug = fields.Str(dump_only=True)
    events = Relationship(
        attribute='event',
        many=True,
        self_view='v1.event_topic_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        related_view_kwargs={'event_topic_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    event_sub_topics = Relationship(
        self_view='v1.event_topic_event_sub_topic',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_sub_topic_list',
        related_view_kwargs={'event_topic_id': '<id>'},
        many=True,
        schema='EventSubTopicSchema',
        type_='event-sub-topic',
    )

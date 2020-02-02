from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema
from marshmallow import validate

from app.api.helpers.utilities import dasherize


class CustomPlaceholderSchema(Schema):
    class Meta:
        type_ = 'custom-placeholder'
        self_view = 'v1.custom_placeholder_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.custom_placeholder_list'
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    original_image_url = fields.Url(required=True, validate=validate.URL(schemes=["https"]))
    thumbnail_image_url = fields.Url(dump_only=True, validate=validate.URL(schemes=["https"]))
    large_image_url = fields.Url(dump_only=True, validate=validate.URL(schemes=["https"]))
    icon_image_url = fields.Url(dump_only=True, validate=validate.URL(schemes=["https"]))
    copyright = fields.String(allow_none=True)
    origin = fields.String(allow_none=True)
    event_sub_topic = Relationship(
        attribute='event_sub_topic',
        self_view='v1.custom_placeholder_event_sub_topic',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_sub_topic_detail',
        related_view_kwargs={'custom_placeholder_id': '<id>'},
        schema='EventSubTopicSchema',
        type_='event-sub-topic',
    )

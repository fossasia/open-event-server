from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.custom_placeholder import CustomPlaceholder
from app.models.event_sub_topic import EventSubTopic
from app.api.helpers.files import create_save_image_sizes


class CustomPlaceholderSchema(Schema):
    class Meta:
        type_ = 'custom-placeholder'
        self_view = 'v1.custom_placeholder_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.custom_placeholder_list'
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    name = fields.String(required=True)
    original_image_url = fields.Url(required=True)
    thumbnail_image_url = fields.Url(dump_only=True)
    large_image_url = fields.Url(dump_only=True)
    icon_image_url = fields.Url(dump_only=True)
    copyright = fields.String(allow_none=True)
    origin = fields.String(allow_none=True)
    event_sub_topic = Relationship(attribute='event_sub_topic',
                                   self_view='v1.custom_placeholder_event_sub_topic',
                                   self_view_kwargs={'id': '<id>'},
                                   related_view='v1.event_sub_topic_detail',
                                   related_view_kwargs={'custom_placeholder_id': '<id>'},
                                   schema='EventSubTopicSchema',
                                   type_='event-sub-topic')


class CustomPlaceholderList(ResourceList):
    """
    List and create event custom placeholders
    """

    def query(self, view_kwargs):
        """
        query method for custom placeholders list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(CustomPlaceholder)
        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query(self, EventSubTopic, 'id', view_kwargs['event_sub_topic_id'],
                                         'event_sub_topic_id')
            query_ = query_.join(EventSubTopic).filter(EventSubTopic.id == event_sub_topic.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query(self, EventSubTopic, 'id', view_kwargs['event_sub_topic_id'],
                                         'event_sub_topic_id')
            data['event_sub_topic_id'] = event_sub_topic.id

    def after_create_object(self, custom_placeholder, data, view_kwargs):
        if data.get('original_image_url'):
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'custom-placeholders',
                                                      custom_placeholder.id)
            self.session.query(CustomPlaceholder).filter_by(id=custom_placeholder.id).update(uploaded_images)

    view_kwargs = True
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = CustomPlaceholderSchema
    data_layer = {'session': db.session,
                  'model': CustomPlaceholder,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class CustomPlaceholderDetail(ResourceDetail):
    """
    custom placeholder detail by id
    """
    def before_get_object(self, view_kwargs):
        event_sub_topic = None
        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query(self, EventSubTopic, 'id', view_kwargs['event_sub_topic_id'],
                                         'event_sub_topic_id')

        if event_sub_topic:
            custom_placeholder = safe_query(self, CustomPlaceholder, 'event_sub_topic_id', event_sub_topic.id,
                                            'event_sub_topic_id')
            view_kwargs['id'] = custom_placeholder.id

    def before_update_object(self, custom_placeholder, data, view_kwargs):
        if data.get('original_image_url') and data['original_image_url'] != custom_placeholder.original_image_url:
            uploaded_images = create_save_image_sizes(data['original_image_url'], 'custom-placeholders',
                                                      custom_placeholder.id)
            data['original_image_url'] = uploaded_images['original_image_url']
            data['large_image_url'] = uploaded_images['large_image_url']
            data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
            data['icon_image_url'] = uploaded_images['icon_image_url']
        else:
            if data.get('large_image_url'):
                del data['large_image_url']
            if data.get('thumbnail_image_url'):
                del data['thumbnail_image_url']
            if data.get('icon_image_url'):
                del data['icon_image_url']

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomPlaceholderSchema
    data_layer = {'session': db.session,
                  'model': CustomPlaceholder,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object
                  }}


class CustomPlaceholderRelationship(ResourceRelationship):
    """
    Relationship
    """
    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomPlaceholderSchema
    data_layer = {'session': db.session,
                  'model': CustomPlaceholder}

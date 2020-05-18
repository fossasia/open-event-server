from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, safe_query_kwargs
from app.api.helpers.files import create_save_image_sizes
from app.api.schema.custom_placeholders import CustomPlaceholderSchema
from app.models import db
from app.models.custom_placeholder import CustomPlaceholder
from app.models.event_sub_topic import EventSubTopic


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
            event_sub_topic = safe_query_kwargs(
                EventSubTopic,
                view_kwargs,
                'event_sub_topic_id',
            )
            query_ = query_.join(EventSubTopic).filter(
                EventSubTopic.id == event_sub_topic.id
            )
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query_kwargs(
                EventSubTopic,
                view_kwargs,
                'event_sub_topic_id',
            )
            data['event_sub_topic_id'] = event_sub_topic.id

    def after_create_object(self, custom_placeholder, data, view_kwargs):
        """
        after create method for custom placeholder to save image sizes
        :param custom_placeholder:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('original_image_url'):
            uploaded_images = create_save_image_sizes(
                data['original_image_url'], 'custom-placeholders', custom_placeholder.id
            )
            self.session.query(CustomPlaceholder).filter_by(
                id=custom_placeholder.id
            ).update(uploaded_images)

    view_kwargs = True
    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = CustomPlaceholderSchema
    data_layer = {
        'session': db.session,
        'model': CustomPlaceholder,
        'methods': {
            'query': query,
            'before_create_object': before_create_object,
            'after_create_object': after_create_object,
        },
    }


class CustomPlaceholderDetail(ResourceDetail):
    """
    custom placeholder detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get object method to get custom placeholder id for detail
        :param view_kwargs:
        :return:
        """
        event_sub_topic = None
        if view_kwargs.get('event_sub_topic_id'):
            event_sub_topic = safe_query_kwargs(
                EventSubTopic,
                view_kwargs,
                'event_sub_topic_id',
            )

        if event_sub_topic:
            custom_placeholder = safe_query(
                CustomPlaceholder,
                'event_sub_topic_id',
                event_sub_topic.id,
                'event_sub_topic_id',
            )
            view_kwargs['id'] = custom_placeholder.id

    def before_update_object(self, custom_placeholder, data, view_kwargs):
        """
        method to update image sizes before updating the custom placeholder
        :param custom_placeholder:
        :param data:
        :param view_kwargs:
        :return:
        """
        if (
            data.get('original_image_url')
            and data['original_image_url'] != custom_placeholder.original_image_url
        ):
            uploaded_images = create_save_image_sizes(
                data['original_image_url'], 'custom-placeholders', custom_placeholder.id
            )
            data['original_image_url'] = uploaded_images['original_image_url']
            data['large_image_url'] = uploaded_images['large_image_url']
            data['thumbnail_image_url'] = uploaded_images['thumbnail_image_url']
            data['icon_image_url'] = uploaded_images['icon_image_url']

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomPlaceholderSchema
    data_layer = {
        'session': db.session,
        'model': CustomPlaceholder,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
        },
    }


class CustomPlaceholderRelationship(ResourceRelationship):
    """
    Relationship
    """

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = CustomPlaceholderSchema
    data_layer = {'session': db.session, 'model': CustomPlaceholder}

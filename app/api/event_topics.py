from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
import urllib.error

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.event_topics import EventTopicSchema
from app.models import db
from app.api.helpers.files import create_system_image
from app.models.event import Event
from app.models.event_sub_topic import EventSubTopic
from app.models.event_topic import EventTopic


class EventTopicList(ResourceList):

    """
    List and create event topics
    """
    def after_create_object(self, event_topic, data, view_kwargs):
        """
        after create method to save roles for users and add the user as an accepted role(organizer)
        :param event_topic:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('system_image_url'):
            try:
                uploaded_image = create_system_image(data['system_image_url'], unique_identifier=event_topic.id)
            except (urllib.error.HTTPError, urllib.error.URLError):
                raise UnprocessableEntity(
                    {'source': 'attributes/system-image-url'}, 'Invalid Image URL'
                )
            except IOError:
                raise UnprocessableEntity(
                    {'source': 'attributes/system-image-url'}, 'Image is absent at URL'
                )
        else:
            try:
                uploaded_image = create_system_image(unique_identifier=event_topic.id)
            except IOError:
                raise UnprocessableEntity(
                    {'source': ''}, 'Default Image is absent in server'
                )

        self.session.query(EventTopic).filter_by(id=event_topic.id).update(uploaded_image)
        self.session.commit()

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic,
                  'methods': {'after_create_object': after_create_object}}


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

    def before_update_object(self, event_topic, data, view_kwargs):
        """
        method to save image urls before updating event object
        :param event_topic:
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('system_image_url'):
            try:
                uploaded_image = create_system_image(data['system_image_url'], unique_identifier=event_topic.id)
            except (urllib.error.HTTPError, urllib.error.URLError):
                raise UnprocessableEntity(
                    {'source': 'attributes/system-image-url'}, 'Invalid Image URL'
                )
            except IOError:
                raise UnprocessableEntity(
                    {'source': 'attributes/system-image-url'}, 'Image is absent at URL'
                )
        else:
            try:
                uploaded_image = create_system_image(unique_identifier=event_topic.id)
            except IOError:
                raise UnprocessableEntity(
                    {'source': ''}, 'Default Image is absent in server'
                )

            data['system_image_url'] = uploaded_image['system_image_url']

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTopicSchema
    data_layer = {'session': db.session,
                  'model': EventTopic,
                  'methods': {
                      'before_update_object': before_update_object,
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

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.schema.event_types import EventTypeSchema
from app.models import db
from app.models.event import Event
from app.models.event_type import EventType


class EventTypeList(ResourceList):

    """
    List and create event types
    """

    decorators = (api.has_permission('is_admin', methods="POST"),)
    schema = EventTypeSchema
    data_layer = {'session': db.session, 'model': EventType}


class EventTypeDetail(ResourceDetail):
    """
    Event type detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
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
            if event.event_type_id:
                view_kwargs['id'] = event.event_type_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTypeSchema
    data_layer = {
        'session': db.session,
        'model': EventType,
        'methods': {'before_get_object': before_get_object},
    }


class EventTypeRelationship(ResourceRelationship):
    """
    Event type Relationship
    """

    decorators = (api.has_permission('is_admin', methods="PATCH,DELETE"),)
    schema = EventTypeSchema
    data_layer = {'session': db.session, 'model': EventType}

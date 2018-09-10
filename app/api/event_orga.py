from flask_rest_jsonapi import ResourceDetail, ResourceRelationship

from app import db
from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.schema.events_orga import EventOrgaSchema
from app.models.event import Event
from app.models.event_orga import EventOrgaModel


class EventOrgaDetail(ResourceDetail):
    """
    Event Orga detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            view_kwargs['id'] = event.id
            view_kwargs['event_id'] = event.id

        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            view_kwargs['id'] = event.id
            view_kwargs['event_id'] = event.id

    decorators = (api.has_permission('is_coorganizer', methods="GET"),)
    schema = EventOrgaSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class EventOrgaRelationship(ResourceRelationship):
    """
    Event Orga Relationship
    """
    decorators = (api.has_permission('is_coorganizer', methods="GET"),)
    schema = EventOrgaSchema
    data_layer = {'session': db.session,
                  'model': EventOrgaModel}

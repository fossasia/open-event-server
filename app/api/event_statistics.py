from flask_rest_jsonapi import ResourceDetail

from app.api.bootstrap import api
from app.api.helpers.db import safe_query_kwargs
from app.api.schema.event_statistics import EventStatisticsGeneralSchema
from app.models import db
from app.models.event import Event


class EventStatisticsGeneralDetail(ResourceDetail):
    """
    Event statistics detail by id
    """

    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id to fetch details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('identifier'):
            event = safe_query_kwargs(Event, view_kwargs, 'identifier', 'identifier')
            view_kwargs['id'] = event.id

    methods = ['GET']
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch="id", fetch_as="event_id", model=Event
        ),
    )
    schema = EventStatisticsGeneralSchema
    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {'before_get_object': before_get_object},
    }

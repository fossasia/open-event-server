from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.station import StationSchema
from app.models import db
from app.models.event import Event
from app.models.microlocation import Microlocation
from app.models.station import Station


class StationList(ResourceList):
    """Create and List Station"""

    @staticmethod
    def query(view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = Station.query
        if view_kwargs.get('event_id'):
            event = safe_query_kwargs(Event, view_kwargs, 'event_id')
            query_ = query_.filter_by(event_id=event.id)

        elif view_kwargs.get('microlocation_id'):
            event = safe_query_kwargs(Microlocation, view_kwargs, 'microlocation_id')
            query_ = query_.filter_by(microlocation_id=event.id)

        return query_

    view_kwargs = True
    schema = StationSchema
    data_layer = {'session': db.session, 'model': Station}


class StationDetail(ResourceDetail):
    """Station detail by id"""

    @staticmethod
    def before_patch(_args, _kwargs, data):
        """
        before patch method
        :param _args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event=data['event']):
            raise ObjectNotFound(
                {'parameter': 'event'},
                f"Event: {data['event']} not found",
            )

        if data['microlocation']:
            require_relationship(['microlocation'], data)
            if not has_access('is_coorganizer', microlocation=data['microlocation']):
                raise ObjectNotFound(
                    {'parameter': 'microlocation'},
                    f"Microlocation: {data['microlocation']} not found",
                )
        else:
            if data['station_type'] != 'registration':
                raise ObjectNotFound(
                    {'parameter': 'microlocation'},
                    "Microlocation: missing from your request.",
                )

    schema = StationSchema
    data_layer = {
        'session': db.session,
        'model': Station,
    }


class StationRelationship(ResourceRelationship):
    """Station Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = StationSchema
    data_layer = {'session': db.session, 'model': Station}


class StationListPost(ResourceList):
    """Create and List Station"""

    @staticmethod
    def before_post(_args, _kwargs, data):
        """
        method to check for required relationship with event and microlocation
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event=data['event']):
            raise ObjectNotFound(
                {'parameter': 'event'},
                f"Event: {data['event']} not found",
            )

        if data['microlocation']:
            require_relationship(['microlocation'], data)
            if not has_access('is_coorganizer', microlocation=data['microlocation']):
                raise ObjectNotFound(
                    {'parameter': 'microlocation'},
                    f"Microlocation: {data['microlocation']} not found",
                )
        else:
            if data['station_type'] != 'registration':
                raise ObjectNotFound(
                    {'parameter': 'microlocation'},
                    "Microlocation: missing from your request.",
                )

    schema = StationSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': Station}

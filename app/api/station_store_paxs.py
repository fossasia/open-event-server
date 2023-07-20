from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import safe_query_kwargs
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import require_relationship
from app.api.schema.station_store_pax import StationStorePaxSchema
from app.models import db
from app.models.session import Session
from app.models.station import Station
from app.models.station_store_pax import StationStorePax


class StationStorePaxList(ResourceList):
    """Create and List Station Store Pax"""

    def query(self, view_kwargs):
        """
        query method for different view_kwargs
        :param view_kwargs:
        :return:
        """
        query_ = StationStorePax.query
        if view_kwargs.get('station_id'):
            station = safe_query_kwargs(Station, view_kwargs, 'station_id')
            query_ = query_.filter_by(station_id=station.id)

        if view_kwargs.get('session_id'):
            session = safe_query_kwargs(Session, view_kwargs, 'session_id')
            query_ = query_.filter_by(session_id=session.id)
        return query_

    view_kwargs = True
    decorators = (jwt_required,)
    methods = [
        'GET',
    ]
    schema = StationStorePaxSchema
    data_layer = {
        'session': db.session,
        'model': StationStorePax,
        'methods': {'query': query},
    }


class StationStorePaxDetail(ResourceDetail):
    """StationStorePax detail by id"""

    @staticmethod
    def before_patch(_args, _kwargs, data):
        """
        before patch method
        :param _args:
        :param kwargs:
        :param data:
        :return:
        """
        if data['station']:
            require_relationship(['station'], data)
            if not has_access('is_coorganizer', station=data['station']):
                raise ObjectNotFound(
                    {'parameter': 'station'},
                    f"Station: {data['station']} not found",
                )

        if data['session']:
            require_relationship(['session'], data)
            if not has_access('is_coorganizer', session=data['session']):
                raise ObjectNotFound(
                    {'parameter': 'session'},
                    f"Session: {data['session']} not found",
                )

    schema = StationStorePaxSchema
    data_layer = {
        'session': db.session,
        'model': StationStorePax,
    }


class StationStorePaxRelationship(ResourceRelationship):
    """StationStorePax Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = StationStorePaxSchema
    data_layer = {'session': db.session, 'model': StationStorePax}


class StationStorePaxListPost(ResourceList):
    """Create and List StationStorePax"""

    @staticmethod
    def before_post(_args, _kwargs, data):
        """
        method to check for required relationship with event and microlocation
        :param data:
        :return:
        """
        if data['station']:
            require_relationship(['station'], data)
            if not has_access('is_coorganizer', station=data['station']):
                raise ObjectNotFound(
                    {'parameter': 'station'},
                    f"Station: {data['station']} not found",
                )

        if data['session']:
            require_relationship(['session'], data)
            if not has_access('is_coorganizer', session=data['session']):
                raise ObjectNotFound(
                    {'parameter': 'session'},
                    f"Session: {data['session']} not found",
                )

    schema = StationStorePaxSchema
    methods = [
        'POST',
    ]
    data_layer = {'session': db.session, 'model': StationStorePax}

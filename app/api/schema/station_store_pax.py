from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class StationStorePaxSchema(Schema):
    """API Schema for Station Store Pax database model"""

    class Meta:
        """Meta class for Station Schema"""

        type_ = 'station-store-pax'
        self_view = 'v1.station_store_pax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    current_pax = fields.Integer(required=True)
    created_at = fields.DateTime(dump_only=True)
    modified_at = fields.DateTime(dump_only=True)
    station = Relationship(
        self_view='v1.station_store_pax_station',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.station_detail',
        related_view_kwargs={'id': '<station_id>'},
        schema='StationSchema',
        type_='station',
    )
    session = Relationship(
        self_view='v1.station_store_pax_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_detail',
        related_view_kwargs={'id': '<session_id>'},
        schema='SessionSchema',
        type_='session',
    )

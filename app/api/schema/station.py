from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.static import STATION_CHOICES
from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class StationSchema(Schema):
    """API Schema for Station database model"""

    class Meta:
        """Meta class for Station Schema"""

        type_ = 'station'
        self_view = 'v1.station_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    station_name = fields.String(required=True, validate=validate.Length(min=1))
    station_type = fields.String(
        required=True, validate=validate.OneOf(choices=STATION_CHOICES)
    )
    microlocation_id = fields.Function(lambda obj: obj.microlocation.id)

    room = fields.Function(lambda obj: obj.microlocation.room)
    event = Relationship(
        self_view='v1.station_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    microlocation = Relationship(
        self_view='v1.station_microlocation',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.microlocation_detail',
        related_view_kwargs={'id': '<microlocation_id>'},
        schema='MicrolocationSchema',
        type_='microlocation',
    )

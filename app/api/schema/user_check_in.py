from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.static import STATION_TYPE
from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class UserCheckInSchema(Schema):
    """API Schema for Station database model"""

    class Meta:
        """Meta class for Station Schema"""

        type_ = 'user_check_in'
        self_view = 'v1.user_check_in_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    success = fields.Boolean(dump_only=True, default=True)
    message = fields.Method("get_check_in_out_status")

    ticket_holder = Relationship(
        self_view='v1.user_check_in_attendee',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.attendee_detail',
        related_view_kwargs={'id': '<id>'},
        schema='AttendeeSchemaPublic',
        type_='attendee',
        load_only=True,
    )
    station = Relationship(
        self_view='v1.user_check_in_station',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.station_detail',
        related_view_kwargs={'id': '<id>'},
        schema='StationSchema',
        type_='station',
        load_only=True,
    )
    session = Relationship(
        self_view='v1.user_check_in_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_detail',
        related_view_kwargs={'id': '<id>'},
        schema='SessionSchema',
        type_='session',
        load_only=True,
    )

    @staticmethod
    def get_check_in_out_status(obj):
        """
        get checkin status
        @param obj:
        @return:
        """
        if obj.station.station_type == STATION_TYPE.get('check in'):
            return "Attendee check in successful."
        if obj.station.station_type == STATION_TYPE.get('check out'):
            return "Attendee check out successful."
        if obj.station.station_type == STATION_TYPE.get('registration'):
            return "Ticket register successful."
        if obj.station.station_type == STATION_TYPE.get('daily'):
            return "Attendee daily check successful."
        return None

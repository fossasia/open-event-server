from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

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
    track_name = fields.String()
    session_name = fields.String()
    speaker_name = fields.String()

    ticket = Relationship(
        self_view='v1.user_check_in_ticket',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_detail',
        related_view_kwargs={'id': '<id>'},
        schema='TicketSchemaPublic',
        type_='ticket',
    )
    ticket_holder = Relationship(
        self_view='v1.user_check_in_attendee',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.attendee_detail',
        related_view_kwargs={'id': '<id>'},
        schema='AttendeeSchemaPublic',
        type_='attendee',
    )
    station = Relationship(
        self_view='v1.user_check_in_station',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.station_detail',
        related_view_kwargs={'id': '<id>'},
        schema='StationSchema',
        type_='station',
    )
    session = Relationship(
        self_view='v1.user_check_in_session',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_detail',
        related_view_kwargs={'id': '<id>'},
        schema='SessionSchema',
        type_='session',
    )

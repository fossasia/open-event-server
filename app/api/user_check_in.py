import datetime

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.static import STATION_TYPE
from app.api.helpers.user_check_in import (
    validate_check_in_out_status,
    validate_microlocation,
)
from app.api.helpers.utilities import require_relationship
from app.api.schema.station import StationSchema
from app.api.schema.user_check_in import UserCheckInSchema
from app.models import db
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.station import Station
from app.models.ticket_holder import TicketHolder
from app.models.track import Track
from app.models.user_check_in import UserCheckIn


class UserCheckInList(ResourceList):
    """Get List User Check In"""

    def query(self, _view_kwargs):
        """
        Retrieve all user check in data
        @param _view_kwargs:
        @return:
        """
        query_ = self.session.query(UserCheckIn)

        return query_

    view_kwargs = True
    schema = StationSchema
    data_layer = {
        'session': db.session,
        'model': UserCheckIn,
        'methods': {'query': query},
    }


class UserCheckInDetail(ResourceDetail):
    """Station detail by id"""

    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = UserCheckInSchema
    data_layer = {
        'session': db.session,
        'model': UserCheckIn,
    }


class UserCheckInRelationship(ResourceRelationship):
    """Station Relationship (Required)"""

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = StationSchema
    data_layer = {'session': db.session, 'model': Station}


class UserCheckInListPost(ResourceList):
    """Create and List Station"""

    @staticmethod
    def before_post(_args, _kwargs, data):
        """
        method to check for required relationship
        :param data:
        :return:
        """
        require_relationship(['station'], data)
        try:
            station = db.session.query(Station).filter_by(id=data.get('station')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': data.get('station')}, "Station: not found")

        require_relationship(['ticket_holder'], data)
        if station.station_type != STATION_TYPE.get('registration') or data.get(
            'session'
        ):
            require_relationship(['session'], data)

    def before_create_object(self, data, _view_kwargs):
        """
        before create object method for UserCheckInListPost Class
        :param data:
        :param _view_kwargs:
        :return:
        """
        try:
            station = db.session.query(Station).filter_by(id=data.get('station')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': data.get('station')}, "Station: not found")
        current_time = datetime.datetime.utcnow()
        if not has_access('is_coorganizer', event_id=station.event_id):
            raise UnprocessableEntityError(
                {'parameter': 'station'},
                "Only admin/organiser/coorganizer of event only able to check in",
            )
        try:
            attendee = (
                self.session.query(TicketHolder)
                .filter_by(id=data.get('ticket_holder'))
                .one()
            )
        except NoResultFound:
            raise ObjectNotFound(
                {'parameter': data.get('attendee')}, "Attendee: not found"
            )

        if attendee.event_id != station.event_id:
            raise UnprocessableEntityError(
                {'parameter': 'Attendee'},
                "Attendee not belong to this event",
            )

        if station.station_type != STATION_TYPE.get('registration'):
            # validate if microlocation_id from session matches with station
            session = (
                self.session.query(Session).filter_by(id=data.get('session')).first()
            )
            if session is None:
                raise ObjectNotFound(
                    {'parameter': data.get('session')}, "Session: not found"
                )
            validate_microlocation(station=station, session=session)
            if session.session_type_id:
                session_type = (
                    self.session.query(SessionType)
                    .filter(SessionType.id == session.session_type_id)
                    .first()
                )
                if session_type is not None:
                    data['session_name'] = session_type.name
            if session.track_id:
                track = (
                    self.session.query(Track).filter(Track.id == session.track_id).first()
                )
                if track is not None:
                    data['track_name'] = track.name
            data['speaker_name'] = ', '.join(
                [str(speaker.name) for speaker in session.speakers]
            )

        if station.station_type in (
            STATION_TYPE.get('check in'),
            STATION_TYPE.get('check out'),
        ):

            attendee_check_in_status = (
                self.session.query(UserCheckIn)
                .filter(
                    UserCheckIn.ticket_holder_id == data.get('ticket_holder'),
                    UserCheckIn.session_id == data.get('session'),
                    UserCheckIn.check_in_out_at >= datetime.datetime.utcnow().date(),
                )
                .order_by(UserCheckIn.check_in_out_at.desc())
                .first()
            )
            validate_check_in_out_status(
                station=station, attendee_data=attendee_check_in_status
            )
            data['check_in_out_at'] = current_time
        else:
            if station.station_type == STATION_TYPE.get('registration'):
                attendee_check_in_status = (
                    self.session.query(UserCheckIn)
                    .filter(
                        UserCheckIn.ticket_holder_id == data.get('ticket_holder'),
                        UserCheckIn.station_id == data.get('station'),
                        UserCheckIn.created_at >= datetime.datetime.utcnow().date(),
                    )
                    .first()
                )
                if attendee_check_in_status:
                    raise UnprocessableEntityError(
                        {
                            'ticket': data.get('ticket'),
                            'station ': data.get('station'),
                        },
                        "Attendee already registered.",
                    )
                # update register time for attendee
                attendee.is_registered = True
                attendee.register_times = current_time
                save_to_db(attendee)
            if station.station_type == STATION_TYPE.get('daily'):
                attendee_check_in_status = (
                    self.session.query(UserCheckIn)
                    .filter(
                        UserCheckIn.ticket_holder_id == data.get('ticket_holder'),
                        UserCheckIn.station_id == data.get('station'),
                        UserCheckIn.session_id == data.get('session'),
                        UserCheckIn.created_at >= datetime.datetime.utcnow().date(),
                    )
                    .first()
                )
                if attendee_check_in_status:
                    raise UnprocessableEntityError(
                        {
                            'ticket_holder': data.get('ticket_holder'),
                            'station ': data.get('station'),
                        },
                        "Attendee already check daily on station.",
                    )

    schema = UserCheckInSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': UserCheckIn,
        'methods': {
            'before_create_object': before_create_object,
        },
    }

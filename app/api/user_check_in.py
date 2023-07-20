import datetime

from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.static import STATION_TYPE
from app.api.helpers.utilities import require_relationship
from app.api.schema.station import StationSchema
from app.api.schema.user_check_in import UserCheckInSchema
from app.models import db
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.station import Station
from app.models.track import Track
from app.models.user_check_in import UserCheckIn


class UserCheckInList(ResourceList):
    """Get List User Check In"""

    def query(self, view_kwargs):
        query_ = UserCheckIn.query

        return query_

    view_kwargs = True
    schema = StationSchema
    data_layer = {
        'session': db.session,
        'model': UserCheckIn,
        'methods': {'query': query},
    }


class UserCheckInDetail(ResourceDetail):
    """
    Station detail by id
    """

    def after_get_object(self, data, view_kwargs):
        if data.session:
            try:
                session = data.session
                if session.session_type_id:
                    session_type = (
                        db.session.query(SessionType)
                        .filter_by(id=session.session_type_id)
                        .one()
                    )
                    data.session_name = session_type.name
                if session.track_id:
                    track = db.session.query(Track).filter_by(id=session.track_id).one()
                    data.track_name = track.name
                if session.speakers:
                    data.speaker_name = session.speakers.name
            except NoResultFound:
                raise ObjectNotFound(
                    {'parameter': data.get('session')}, "Session: not found"
                )

    @staticmethod
    def before_patch(_args, kwargs, data):
        pass

    #     require_relationship(['event'], data)
    #     if not has_access('is_coorganizer', event=data['event']):
    #         raise ObjectNotFound(
    #             {'parameter': 'event'},
    #             f"Event: {data['event']} not found",
    #         )
    #
    #     if data['microlocation']:
    #         require_relationship(['microlocation'], data)
    #         if not has_access('is_coorganizer', microlocation=data['microlocation']):
    #             raise ObjectNotFound(
    #                 {'parameter': 'microlocation'},
    #                 f"Microlocation: {data['microlocation']} not found",
    #             )
    #     else:
    #         if data['station_type'] != 'registration':
    #             raise ObjectNotFound(
    #                 {'parameter': 'microlocation'},
    #                 f"Microlocation: missing from your request.",
    #             )
    #
    methods = ['GET', 'DELETE']
    decorators = (jwt_required,)
    schema = UserCheckInSchema
    data_layer = {
        'session': db.session,
        'model': UserCheckIn,
        'methods': {
            'after_get_object': after_get_object,
        },
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
    def before_post(args, kwargs, data):
        """
        method to check for required relationship
        :param data:
        :return:
        """
        require_relationship(['station'], data)
        if not has_access('is_coorganizer', station=data.get('station')):
            raise ObjectNotFound(
                {'parameter': 'station'},
                f"Station: {data['station']} not found",
            )
        # require_relationship(['ticket_holder'], data)
        # if not has_access('is_coorganizer', ticket_holder=data.get('ticket_holder')):
        #     raise ObjectNotFound(
        #         {'parameter': 'ticket_holder'},
        #         f"TicketHolder: {data['ticket_holder']} not found",
        #     )
        try:
            station = db.session.query(Station).filter_by(id=data.get('station')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': data.get('station')}, "Station: not found")

        if station.station_type == 'registration' or data.get('ticket'):
            require_relationship(['ticket'], data)
            if not has_access('is_coorganizer', ticket=data.get('ticket')):
                raise ObjectNotFound(
                    {'parameter': 'ticket'},
                    f"Ticket: {data['ticket']} not found",
                )
        if station.station_type != STATION_TYPE.get('registration') or data.get(
            'session'
        ):
            require_relationship(['session'], data)
            if not has_access('is_coorganizer', session=data.get('session')):
                raise ObjectNotFound(
                    {'parameter': 'session'},
                    f"Session: {data['session']} not found",
                )
        if station.station_type != STATION_TYPE.get('registration') or data.get(
            'ticket_holder'
        ):
            require_relationship(['ticket_holder'], data)
            if not has_access('is_coorganizer', ticket_holder=data.get('ticket_holder')):
                raise ObjectNotFound(
                    {'parameter': 'ticket_holder'},
                    f"TicketHolder: {data['ticket_holder']} not found",
                )

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for UserCheckInListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        try:
            station = self.session.query(Station).filter_by(id=data.get('station')).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': data.get('station')}, "Station: not found")
        if station.station_type != STATION_TYPE.get('registration'):
            # validate if microlocation_id from session matches microlocation_id from station
            try:
                session = (
                    self.session.query(Session).filter_by(id=data.get('session')).one()
                )
            except NoResultFound:
                raise ObjectNotFound(
                    {'parameter': data.get('station')}, "Station: not found"
                )
            if station.microlocation_id != session.microlocation_id:
                raise UnprocessableEntityError(
                    {
                        'station microlocation': station.microlocation_id,
                        'session microlocation': session.microlocation_id,
                    },
                    "Location of your session not matches with station location"
                    ", please check with the organizer.",
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
                    )
                    .order_by(UserCheckIn.check_in_out_at.desc())
                    .first()
                )
                if attendee_check_in_status:
                    if (
                        attendee_check_in_status.station.station_type
                        == station.station_type
                        and station.station_type == STATION_TYPE.get('check in')
                    ) and attendee_check_in_status.check_in_out_at.date() == datetime.datetime.now().date():
                        raise UnprocessableEntityError(
                            {
                                'attendee': data.get('ticket_holder'),
                                'session ': data.get('session'),
                            },
                            "Attendee already checked in.",
                        )
                    if (
                        attendee_check_in_status.station.station_type
                        == station.station_type
                        and station.station_type == STATION_TYPE.get('check out')
                    ):
                        raise UnprocessableEntityError(
                            {
                                'attendee': data.get('ticket_holder'),
                                'session ': data.get('session'),
                            },
                            "Attendee not check in yet.",
                        )
                else:
                    if station.station_type == STATION_TYPE.get('check out'):
                        raise UnprocessableEntityError(
                            {
                                'attendee': data.get('ticket_holder'),
                                'session ': data.get('session'),
                            },
                            "Attendee not check in yet.",
                        )
            else:
                if station.station_type == STATION_TYPE.get('registration'):
                    attendee_check_in_status = (
                        self.session.query(UserCheckIn)
                        .filter(UserCheckIn.ticket_id == data.get('ticket'))
                        .first()
                    )
                    if attendee_check_in_status:
                        raise UnprocessableEntityError(
                            {
                                'ticket': data.get('ticket'),
                                'station ': data.get('station'),
                            },
                            "Ticket already registed on station.",
                        )
                if station.station_type == STATION_TYPE.get('daily'):
                    attendee_check_in_status = (
                        self.session.query(UserCheckIn)
                        .filter(
                            UserCheckIn.ticket_holder_id == data.get('ticket_holder'),
                            UserCheckIn.session_id == data.get('session'),
                        )
                        .order_by(UserCheckIn.check_in_out_at.desc())
                        .first()
                    )
                    if attendee_check_in_status:
                        raise UnprocessableEntityError(
                            {
                                'ticket': data.get('ticket'),
                                'station ': data.get('station'),
                            },
                            "Ticket already registed on station.",
                        )

        if station.station_type in (
            STATION_TYPE.get('check in'),
            STATION_TYPE.get('check out'),
        ):
            data['check_in_out_at'] = datetime.datetime.utcnow()

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

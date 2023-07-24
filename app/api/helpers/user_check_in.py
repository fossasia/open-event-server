from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.static import STATION_TYPE
from app.models.session import Session
from app.models.station import Station
from app.models.user_check_in import UserCheckIn


def validate_microlocation(station: Station, session: Session):
    """
    validate if microlocation matches
    @param station:
    @param session:
    """
    if station.microlocation_id != session.microlocation_id:
        raise UnprocessableEntityError(
            {
                'station microlocation': station.microlocation_id,
                'session microlocation': session.microlocation_id,
            },
            "Location of your session not matches with station location"
            ", please check with the organizer.",
        )


def validate_check_in_out_status(station: Station, attendee_data: UserCheckIn):
    """
    validate if attendee already check in/out
    @param station:
    @param attendee_data:
    """
    if attendee_data:
        if (
            attendee_data.station.station_type == station.station_type
            and station.station_type == STATION_TYPE.get('check in')
        ):
            raise UnprocessableEntityError(
                {
                    'attendee': attendee_data.ticket_holder_id,
                    'session ': attendee_data.session_id,
                },
                "Attendee already checked in.",
            )
        if (
            attendee_data.station.station_type == station.station_type
            and station.station_type == STATION_TYPE.get('check out')
        ):
            raise UnprocessableEntityError(
                {
                    'attendee': attendee_data.ticket_holder_id,
                    'session ': attendee_data.session_id,
                },
                "Attendee not check in yet.",
            )
    else:
        if station.station_type == STATION_TYPE.get('check out'):
            raise UnprocessableEntityError(
                {
                    'attendee': attendee_data.ticket_holder_id,
                    'session ': attendee_data.session_id,
                },
                "Attendee not check in yet.",
            )

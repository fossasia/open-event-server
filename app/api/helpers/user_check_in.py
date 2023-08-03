import csv
import os
import uuid
from datetime import datetime, timedelta

from flask import current_app

from app.api.helpers.errors import BadRequestError, UnprocessableEntityError
from app.api.helpers.static import STATION_TYPE
from app.api.helpers.storage import UPLOAD_PATHS, UploadedFile, generate_hash, upload
from app.models.session import Session
from app.models.station import Station
from app.models.user_check_in import UserCheckIn


def export_csv(data):
    if data is None:
        raise BadRequestError({'source': data}, 'Bad Request Error')

    query_ = UserCheckIn.query.join(Station)
    if 'session_id' in data and data['session_id']:
        query_ = query_.filter(UserCheckIn.session_id == data['session_id'])
    if 'date' in data and data['date']:
        dt = datetime.strptime(data['date'], '%Y-%m-%d')
        start = dt - timedelta(0)
        end = start + timedelta(days=1)
        query_ = query_.filter(UserCheckIn.created_at >= start).filter(
            UserCheckIn.created_at < end
        )
    if 'track_type' in data and data['track_type']:
        query_ = query_.filter(UserCheckIn.track_name == data['track_type'])
    if 'type' in data and data['type']:
        if '&' in data['type']:
            query_ = query_.filter(
                Station.station_type.in_(x.strip() for x in data['type'].split('&'))
            )
        else:
            query_ = query_.filter(Station.station_type == data['type'])
    userCheckIns = query_.order_by(UserCheckIn.created_at.desc()).all()

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)

        identifier = uuid.uuid1().hex
        filename = f"user-check-in-{identifier}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            content = create_file_csv(userCheckIns)
            for row in content:
                writer.writerow(row)
        csv_file = UploadedFile(file_path=file_path, filename=filename)
        uploadPath = UPLOAD_PATHS['exports-temp']['csv'].format(
            event_id='admin', identifier=identifier
        )
        upload(csv_file, uploadPath)
        os.remove(filedir + filename)
        return f'static/media/{uploadPath}/{generate_hash(uploadPath)}/{filename}'
    except Exception as e:
        raise BadRequestError({'source': e}, 'Bad Request Error')


def create_file_csv(userCheckIns):
    headers = [
        'Ticket Id',
        'Date Time',
        'Track Name',
        'Session Name',
        'Speaker Name',
        'Type',
    ]

    columns = [
        'ticket_holder_id',
        'created_at',
        'track_name',
        'session_name',
        'speaker_name',
        'type',
    ]
    rows = [headers]
    for userCheckIn in userCheckIns:
        data = []
        for column in columns:
            if column == 'type':
                data.append(userCheckIn.station.station_type)
                continue
            if column == 'created_at':
                data.append(userCheckIn.created_at.strftime('%Y-%m-%d %H:%M:%S'))
                continue
            data.append(getattr(userCheckIn, column))
        rows.append(data)

    return rows


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
    if station.event_id != session.event_id:
        raise UnprocessableEntityError(
            {
                'station event_id': station.event_id,
                'session event_id': session.event_id,
            },
            "Session not belong to this event.",
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

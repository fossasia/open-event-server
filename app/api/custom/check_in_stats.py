import datetime

from flask import Blueprint, request
from sqlalchemy import asc, desc, func

from app.api.helpers.permissions import jwt_required
from app.api.helpers.static import STATION_TYPE
from app.models import db
from app.models.event import Event
from app.models.session import Session
from app.models.session_type import SessionType
from app.models.station import Station
from app.models.station_store_pax import StationStorePax
from app.models.ticket_holder import TicketHolder
from app.models.track import Track
from app.models.user_check_in import UserCheckIn

check_in_stats_routes = Blueprint(
    'check_in_stats_routes', __name__, url_prefix='/v1/user-check-in/stats'
)


@check_in_stats_routes.route('/event/<int:event_id>', methods=['GET'])
@jwt_required
def get_registration_stats(event_id):
    """
    API for get event check in/out stats
    @param event_id: event id to check
    @return: stats
    """
    # check if event is existed
    event = Event.query.filter(Event.id == event_id).first()
    total_attendee = TicketHolder.query.filter(TicketHolder.event_id == event_id).count()
    if event is None:
        return {"message": "Event can not be found."}, 404
    stations = Station.query.filter(Station.event_id == event_id).all()
    registration_stations = [
        station.id
        for station in stations
        if station.station_type == STATION_TYPE.get('registration')
    ]
    check_in_stations = [
        station.id
        for station in stations
        if station.station_type == STATION_TYPE.get('check in')
    ]
    check_out_stations = [
        station.id
        for station in stations
        if station.station_type == STATION_TYPE.get('check out')
    ]
    data = {
        "total_attendee": total_attendee,
        "registration_stations": registration_stations,
        "check_in_stations": check_in_stations,
        "check_out_stations": check_out_stations,
    }

    if request.args.get('today_only'):
        results = {}
        date = datetime.date.today().strftime("%Y-%m-%d")
        data["date"] = date
        results[date] = get_data_by_date(data)
    else:
        stationIds = []
        for station in stations:
            stationIds.append(station.id)
        date_list = list(
            zip(
                *db.session.query(func.date(UserCheckIn.created_at))
                .distinct()
                .filter(
                    UserCheckIn.station_id.in_(stationIds),
                )
                .order_by(asc(func.date(UserCheckIn.created_at)))
                .all()
            )
        )
        dates = list(
            map(
                str,
                date_list[0] if date_list else [],
            )
        )

        if len(dates) == 0:
            return { "2023-10-17": {
                "total_attendee": total_attendee,
                "total_registered": 0,
                "total_not_checked_in": total_attendee - 0,
                "total_track_checked_in": 0,
                "total_track_checked_out": 0,
                "total_session_checked_in": 0,
                "total_session_checked_out": 0,
                "track_stats": [],
                "session_stats": [
                    {
                        "check_in": 0,
                        "check_out": 0,
                        "manual_count": {},
                        "session_id": request.args.get('session_ids'),
                        "session_name": "",
                        "speakers": [],
                        "track_name": "",
                    }
                ],
            }}, 200

        results = {}
        for date in dates:
            data["date"] = date
            results[date] = get_data_by_date(data)
    return results, 200


def get_data_by_date(data):
    """
    Get data by date
    @param data
    @return: result
    """
    registered_attendee = (
        UserCheckIn.query.with_entities(UserCheckIn.ticket_holder_id)
        .filter(
            UserCheckIn.station_id.in_(data['registration_stations']),
            func.date(UserCheckIn.created_at) == data['date'],
        )
        .group_by(UserCheckIn.ticket_holder_id)
        .count()
    )

    check_in_attendee = UserCheckIn.query.filter(
        UserCheckIn.station_id.in_(data['check_in_stations']),
        func.date(UserCheckIn.created_at) == data['date'],
    )

    check_out_attendee = UserCheckIn.query.filter(
        UserCheckIn.station_id.in_(data['check_out_stations']),
        func.date(UserCheckIn.created_at) == data['date'],
    )

    session_checked_in = check_in_attendee.with_entities(
        UserCheckIn.session_id, UserCheckIn.ticket_holder_id
    ).group_by(UserCheckIn.session_id, UserCheckIn.ticket_holder_id)

    session_checked_out = check_out_attendee.with_entities(
        UserCheckIn.session_id, UserCheckIn.ticket_holder_id
    ).group_by(UserCheckIn.session_id, UserCheckIn.ticket_holder_id)

    session_checked_in_count = session_checked_in.count()

    session_checked_out_count = session_checked_out.count()

    track_checked_in = db.session.query(UserCheckIn, Session).filter(
        Session.id.in_(
            [user_check_in.session_id for user_check_in in session_checked_in]
        ),
        UserCheckIn.station_id.in_(data['check_in_stations']),
        Session.id == UserCheckIn.session_id,
        func.date(UserCheckIn.created_at) == data['date'],
    )

    track_checked_in_count = (
        track_checked_in.with_entities(UserCheckIn.ticket_holder_id, Session.track_id)
        .group_by(UserCheckIn.ticket_holder_id, Session.track_id)
        .count()
    )

    track_checked_out = db.session.query(UserCheckIn, Session).filter(
        Session.id.in_(
            [user_check_in.session_id for user_check_in in session_checked_out]
        ),
        UserCheckIn.station_id.in_(data['check_out_stations']),
        UserCheckIn.session_id == Session.id,
        func.date(UserCheckIn.created_at) == data['date'],
    )

    track_checked_out_count = (
        track_checked_out.with_entities(UserCheckIn.ticket_holder_id, Session.track_id)
        .group_by(UserCheckIn.ticket_holder_id, Session.track_id)
        .count()
    )
    session_stat = []
    track_stat = []
    if request.args.get('session_ids'):
        session_stat = get_session_stats(
            request.args.get('session_ids'),
            session_checked_in,
            session_checked_out,
            data['date'],
        )
    if request.args.get('track_ids'):
        track_stat = get_track_stats(
            request.args.get('track_ids'),
            check_in_attendee,
            check_out_attendee,
            data['date'],
        )
    return {
        "total_attendee": data['total_attendee'],
        "total_registered": registered_attendee,
        "total_not_checked_in": data['total_attendee'] - registered_attendee,
        "total_track_checked_in": track_checked_in_count,
        "total_track_checked_out": track_checked_out_count,
        "total_session_checked_in": session_checked_in_count,
        "total_session_checked_out": session_checked_out_count,
        "session_stats": session_stat,
        "track_stats": track_stat,
    }


def get_session_stats(session_ids, session_checked_in, session_checked_out, date):
    """
    Get session stats
    @param session_ids: session id to get
    @param session_checked_in: session_checked_in
    @param session_checked_out: session_checked_out
    @return: list of session stats
    """
    session_stat = []
    session_ids = [session_id.strip() for session_id in session_ids.split(",")]
    for session_id in session_ids:
        speakers = db.session.query(Session).filter(Session.id == session_id).first()
        if speakers:
            current_speakers = [str(speaker.name) for speaker in speakers.speakers]
        else:
            break
        session_check_in = session_checked_in.filter(
            UserCheckIn.session_id == session_id
        ).count()
        session_check_out = session_checked_out.filter(
            UserCheckIn.session_id == session_id
        ).count()
        current_session = (
            db.session.query(Session, SessionType)
            .filter(Session.id == session_id, Session.session_type_id == SessionType.id)
            .with_entities(SessionType.name)
            .first()
        )
        session_name = ''
        if current_session:
            session_name = current_session._asdict()['name']
        current_track = (
            db.session.query(Session, Track)
            .filter(Session.id == session_id, Session.track_id == Track.id)
            .with_entities(Track.name)
            .first()
        )
        track_name = ''
        if current_track:
            track_name = current_track._asdict()['name']

        stationStorePaxs = (
            db.session.query(StationStorePax)
            .filter(
                StationStorePax.session_id == session_id,
                func.date(StationStorePax.created_at) == date,
            )
            .order_by(desc("created_at"))
            .all()
        )
        manual_count = {}
        if stationStorePaxs:
            pax = stationStorePaxs[0]
            manual_count = {
                "current_pax": pax.current_pax,
                "created_at": pax.created_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
                "modified_at": pax.modified_at.strftime("%Y-%m-%dT%H:%M:%S%z"),
            }

        session_stat.append(
            {
                "session_id": session_id,
                "session_name": session_name,
                "track_name": track_name,
                "speakers": current_speakers,
                "check_in": session_check_in,
                "check_out": session_check_out,
                "manual_count": manual_count,
            }
        )
    return session_stat


def get_track_stats(track_ids, check_in_attendee, check_out_attendee, current_time):
    """
    get track stats
    @param track_ids: track_ids
    @param check_in_attendee: check_in_attendee
    @param check_out_attendee: check_out_attendee
    @param current_time: current_time
    @return: list of track stats
    """
    track_stat = []
    track_ids = [session_id.strip() for session_id in track_ids.split(",")]
    for track_id in track_ids:
        current_track = Track.query.filter(Track.id == track_id).first()
        if current_track:
            track_name = current_track.name
        else:
            break
        track_checked_in = db.session.query(UserCheckIn, Session).filter(
            Session.id.in_(
                [user_check_in.session_id for user_check_in in check_in_attendee]
            ),
            UserCheckIn.id.in_([user_check_in.id for user_check_in in check_in_attendee]),
            Session.id == UserCheckIn.session_id,
            func.date(UserCheckIn.created_at) == current_time,
            Session.track_id == track_id,
        )

        track_checked_in_count = (
            track_checked_in.with_entities(UserCheckIn.ticket_holder_id, Session.track_id)
            .group_by(UserCheckIn.ticket_holder_id, Session.track_id)
            .count()
        )

        track_checked_out = db.session.query(UserCheckIn, Session).filter(
            Session.id.in_(
                [user_check_in.session_id for user_check_in in check_out_attendee]
            ),
            UserCheckIn.id.in_(
                [user_check_in.id for user_check_in in check_out_attendee]
            ),
            UserCheckIn.session_id == Session.id,
            func.date(UserCheckIn.created_at) == current_time,
            Session.track_id == track_id,
        )

        track_checked_out_count = (
            track_checked_out.with_entities(
                UserCheckIn.ticket_holder_id, Session.track_id
            )
            .group_by(UserCheckIn.ticket_holder_id, Session.track_id)
            .count()
        )

        current_session = Session.query.filter(
            Session.track_id == track_id,
            Session.starts_at <= datetime.datetime.utcnow(),
            Session.ends_at >= datetime.datetime.utcnow(),
        ).first()
        current_speakers = ''
        session_name = ''
        if current_session:
            current_speakers = [str(speaker.name) for speaker in current_session.speakers]
            current_session_name = (
                db.session.query(Session, SessionType)
                .filter(
                    Session.id == current_session.id,
                    Session.session_type_id == SessionType.id,
                )
                .with_entities(SessionType.name)
                .first()
            )
            session_name = ''
            if current_session:
                session_name = current_session_name._asdict()['name']

        track_stat.append(
            {
                "track_id": track_id,
                "track_name": track_name,
                "current_speakers": current_speakers,
                "current_session": session_name,
                "check_in": track_checked_in_count,
                "check_out": track_checked_out_count,
            }
        )
    return track_stat

import json

from tests.factories.attendee import AttendeeOrderTicketSubFactory, AttendeeSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory
from tests.factories.session import SessionSubFactory
from tests.factories.station import StationSubFactory
from tests.factories.ticket import TicketSubFactory


def get_minimal_attendee(db, user):
    """
    create attendee
    @param db: db
    @param user: user
    @return: attendee created
    """
    attendee = AttendeeOrderTicketSubFactory(
        email=None, address=None, city=None, state=None, country=None, order__user=user
    )
    db.session.commit()

    return attendee


def test_attendee_not_register_yet(db, client, jwt, user):
    """
    Testing for case attendee not register yet
    @param db: db
    @param client: client
    @param jwt: jwt
    @param user: user
    """
    attendee = get_minimal_attendee(db, user)
    data = {'event_id': attendee.event_id, 'attendee_id': attendee.id}
    response = client.get(
        '/v1/states',
        content_type='application/json',
        headers=jwt,
        query_string=data,
    )
    assert response.status_code == 200
    assert json.loads(response.data)['is_registered'] is False


def test_attendee_registered(db, client, jwt, user):
    """
    Test user is already registered
    @param db: db
    @param client: client
    @param jwt: jwt
    @param user: user
    """
    user.is_super_admin = True
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(event=event)
    ticket = TicketSubFactory(event=event)
    station = StationSubFactory(
        event=event, microlocation=microlocation, station_type='registration'
    )
    session = SessionSubFactory(
        event=event,
        microlocation=microlocation,
    )
    attendee = AttendeeSubFactory(
        event=event,
        ticket=ticket,
    )
    db.session.commit()
    data = json.dumps(
        {
            "data": {
                "type": "user_check_in",
                "attributes": {},
                "relationships": {
                    "station": {"data": {"id": str(station.id), "type": "station"}},
                    "session": {"data": {"id": str(session.id), "type": "session"}},
                    "ticket_holder": {
                        "data": {"id": str(attendee.id), "type": "attendee"}
                    },
                },
            }
        }
    )

    client.post(
        '/v1/user-check-in',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    data = {'event_id': event.id, 'attendee_id': attendee.id}

    response = client.get(
        '/v1/states',
        content_type='application/json',
        headers=jwt,
        query_string=data,
    )
    assert response.status_code == 200
    assert json.loads(response.data)['is_registered'] is True

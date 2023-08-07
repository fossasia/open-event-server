import json

from tests.factories.attendee import AttendeeOrderTicketSubFactory, AttendeeSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory
from tests.factories.session import SessionSubFactory
from tests.factories.station import StationSubFactory
from tests.factories.ticket import TicketSubFactory


def get_minimal_attendee(db, user):
    attendee = AttendeeOrderTicketSubFactory(
        email=None, address=None, city=None, state=None, country=None, order__user=user
    )
    db.session.commit()

    return attendee


def test_attendee_not_register_yet(db, client, jwt, user):
    attendee = get_minimal_attendee(db, user)
    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees/{attendee.id}/state',
        content_type='application/vnd.api+json',
        headers=jwt,
    )
    assert response.status_code == 200
    assert json.loads(response.data)['is_registered'] is False


def test_attendee_registered(db, client, jwt, user):
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

    response = client.get(
        f'/v1/events/{event.id}/attendees/{attendee.id}/state',
        content_type='application/vnd.api+json',
        headers=jwt,
    )
    assert response.status_code == 200
    assert json.loads(response.data)['is_registered'] is True

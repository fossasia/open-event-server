import json

from tests.factories.attendee import AttendeeSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory
from tests.factories.session import SessionSubFactory
from tests.factories.station import StationSubFactory
from tests.factories.ticket import TicketFactory


def test_create_station_from_user_check_in(db, client, jwt, user):
    """Test that we can create a new station from a user check in"""
    user.is_super_admin = True
    event = EventFactoryBasic()
    microlocation = MicrolocationSubFactory(
        event=event,
    )
    ticket = TicketFactory(
        event=event,
    )
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

    response = client.post(
        '/v1/user-check-in',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    assert response.json['data']['type'] == 'user_check_in'
    assert response.json['data']['id'] is not None

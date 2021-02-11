import json

from tests.factories.event import EventFactoryBasic
from tests.factories.session import SessionSubFactory


def get_event(db):
    event = EventFactoryBasic(
        starts_at="2199-10-01T1:00:00+00:00", ends_at="2199-10-10T1:00:00+00:00"
    )

    SessionSubFactory(
        event=event,
        starts_at="2199-10-02T1:00:00+00:00",
        ends_at="2199-10-02T1:00:30+00:00",
    )
    SessionSubFactory(
        event=event,
        starts_at="2199-10-02T1:05:00+00:00",
        ends_at="2199-10-02T1:05:30+00:00",
    )
    SessionSubFactory(
        event=event,
        starts_at="2199-10-04T1:00:00+00:00",
        ends_at="2199-10-04T1:00:30+00:00",
    )

    db.session.commit()

    return event


def test_event_session_distinct_dates(db, client):
    event = get_event(db)

    response = client.get(f'/v1/events/{event.id}/sessions/dates')

    assert response.status_code == 200
    assert json.loads(response.data) == ["2199-10-02", "2199-10-04"]

    response = client.get(f'/v1/events/{event.identifier}/sessions/dates')

    assert response.status_code == 200
    assert json.loads(response.data) == ["2199-10-02", "2199-10-04"]

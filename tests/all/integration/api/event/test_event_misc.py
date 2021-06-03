import json

from tests.factories.attendee import AttendeeOrderSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def test_event_no_stream(db, client):
    event = EventFactoryBasic(state='published')
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == {"can_access": False, "exists": False}


def test_event_stream(db, client):
    event = EventFactoryBasic(state='published')
    VideoStreamFactoryBase(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == {"can_access": False, "exists": True}


def test_event_stream_identifier(db, client):
    event = EventFactoryBasic(state='published')
    VideoStreamFactoryBase(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.identifier}/has-streams')

    assert json.loads(response.data) == {"can_access": False, "exists": True}


def test_event_stream_rooms(db, client):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == {"can_access": False, "exists": True}


def test_event_stream_rooms_identifier(db, client):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.identifier}/has-streams')

    assert json.loads(response.data) == {"can_access": False, "exists": True}


def test_event_stream_access(db, client, user, jwt):
    event = EventFactoryBasic(state='published')
    VideoStreamFactoryBase(event=event)
    AttendeeOrderSubFactory(event=event, email=user.email, order__status='completed')
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams', headers=jwt)

    assert json.loads(response.data) == {"can_access": True, "exists": True}


def test_event_stream_rooms(db, client, user, jwt):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    AttendeeOrderSubFactory(event=event, email=user.email, order__status='completed')
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams', headers=jwt)

    assert json.loads(response.data) == {"can_access": True, "exists": True}


def test_event_stream_rooms_identifier(db, client, user, jwt):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    AttendeeOrderSubFactory(event=event, email=user.email, order__status='completed')
    db.session.commit()

    response = client.get(f'/v1/events/{event.identifier}/has-streams', headers=jwt)

    assert json.loads(response.data) == {"can_access": True, "exists": True}


def test_event_stream_rooms_no_access(db, client, jwt):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams', headers=jwt)

    assert json.loads(response.data) == {"can_access": False, "exists": True}

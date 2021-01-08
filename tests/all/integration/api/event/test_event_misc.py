import json

from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def test_event_no_stream(db, client):
    event = EventFactoryBasic(state='published')
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == False


def test_event_stream(db, client):
    event = EventFactoryBasic(state='published')
    VideoStreamFactoryBase(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == True


def test_event_stream_rooms(db, client):
    event = EventFactoryBasic(state='published')
    MicrolocationSubVideoStreamFactory(event=event)
    db.session.commit()

    response = client.get(f'/v1/events/{event.id}/has-streams')

    assert json.loads(response.data) == True

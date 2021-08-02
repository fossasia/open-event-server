import json

import pytest

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.attendee import AttendeeOrderSubFactory
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.session import SessionSubFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def get_room_session_stream(db, user=None, **kwargs):
    stream = VideoStreamFactoryBase(**kwargs)
    room = MicrolocationSubVideoStreamFactory(video_stream=stream)
    session = SessionSubFactory(microlocation=room, event=room.event)
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=room.event, role=role)
    db.session.commit()

    return room, stream, session


def test_stream_get_admin(db, client, admin_jwt):
    room, stream, session = get_room_session_stream(db, name='Test Stream')

    # Access by ID
    response = client.get(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(stream.id)
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room
    response = client.get(
        f'/v1/microlocations/{room.id}/video-stream',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room Include
    response = client.get(
        f'/v1/microlocations/{room.id}?include=video-stream',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][0]['attributes']['name'] == 'Test Stream'

    # Access by Session Include
    response = client.get(
        f'/v1/sessions/{session.id}?include=microlocation.video-stream',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][1]['attributes']['name'] == 'Test Stream'


def test_stream_get_owner(db, client, user, jwt):
    room, stream, session = get_room_session_stream(db, user, name='Test Stream')

    # Access by ID
    response = client.get(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(stream.id)
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room
    response = client.get(
        f'/v1/microlocations/{room.id}/video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room Include
    response = client.get(
        f'/v1/microlocations/{room.id}?include=video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][0]['attributes']['name'] == 'Test Stream'

    # Access by Session Include
    response = client.get(
        f'/v1/sessions/{session.id}?include=microlocation.video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][1]['attributes']['name'] == 'Test Stream'


@pytest.mark.parametrize('order_status', ['completed', 'placed'])
def test_stream_get_attendee(db, client, user, jwt, order_status):
    room, stream, session = get_room_session_stream(db, name='Test Stream')
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(event=room.event, order__status=order_status, email=email)
    db.session.commit()

    # Access by ID
    response = client.get(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(stream.id)
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room
    response = client.get(
        f'/v1/microlocations/{room.id}/video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['name'] == 'Test Stream'

    # Access by Room Include
    response = client.get(
        f'/v1/microlocations/{room.id}?include=video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][0]['attributes']['name'] == 'Test Stream'

    # Access by Session Include
    response = client.get(
        f'/v1/sessions/{session.id}?include=microlocation.video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['included'][1]['attributes']['name'] == 'Test Stream'


@pytest.mark.parametrize('order_status', ['expired', 'pending', 'initializing'])
def test_stream_get_attendee_error(db, client, user, jwt, order_status):
    room, stream, session = get_room_session_stream(db, name='Test Stream')
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(event=room.event, order__status=order_status, email=email)
    db.session.commit()

    # Access by ID
    response = client.get(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    # Access by Room
    response = client.get(
        f'/v1/microlocations/{room.id}/video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    # Access by Room Include
    response = client.get(
        f'/v1/microlocations/{room.id}?include=video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data).get('included') is None

    # Access by Session Include
    response = client.get(
        f'/v1/sessions/{session.id}?include=microlocation.video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['included']) == 1


def test_stream_get_user_error(db, client, jwt):
    room, stream, session = get_room_session_stream(db, name='Test Stream')

    # Access by ID
    response = client.get(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    # Access by Room
    response = client.get(
        f'/v1/microlocations/{room.id}/video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    # Access by Room Include
    response = client.get(
        f'/v1/microlocations/{room.id}?include=video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data).get('included') is None

    # Access by Session Include
    response = client.get(
        f'/v1/sessions/{session.id}?include=microlocation.video-stream',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['included']) == 1

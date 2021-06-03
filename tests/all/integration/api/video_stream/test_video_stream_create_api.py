import json

from app.api.helpers.db import get_or_create
from app.models import event
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from app.models.video_stream import VideoStream
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubFactory


def get_room(db, user=None, **kwargs):
    room = MicrolocationSubFactory(**kwargs)
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=room.event, role=role)
    db.session.commit()

    return room


def test_create_without_room_error(db, client, admin_jwt):
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {"url": "https://meet.jit.si", "name": "Test"},
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 422
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "A valid relationship with either of resources is required: ['rooms', 'event']"
    )


def test_create_with_room_admin(db, client, admin_jwt):
    room = get_room(db)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {"data": [{"id": str(room.id), "type": "microlocation"}]}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_create_with_room_organizer(db, client, user, jwt):
    room = get_room(db, user=user)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {"data": [{"id": str(room.id), "type": "microlocation"}]}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_create_with_rooms_different_events_error(db, client, user, jwt):
    room = get_room(db, user=user)
    room_other = get_room(db, user=user)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(room_other.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403

    assert (
        json.loads(response.data)['errors'][0]['detail']
        == 'Video Stream can only be created/edited with rooms of a single event'
    )


def test_create_with_rooms_same_events(db, client, user, jwt):
    room = get_room(db, user=user)
    room_other = get_room(db, event=room.event)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(room_other.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'

    response = client.get(
        f'/v1/video-streams/{stream.id}/rooms',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    response_dict = json.loads(response.data)
    assert response_dict['data'][0]['id'] == str(room.id)
    assert response_dict['data'][1]['id'] == str(room_other.id)


def test_create_with_room_user_error(db, client, jwt):
    room = get_room(db)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {"data": [{"id": str(room.id), "type": "microlocation"}]}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403

    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def get_event(db, user=None, **kwargs):
    event = EventFactoryBasic(**kwargs)
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    return event


def test_create_with_event_admin(db, client, admin_jwt):
    event = get_event(db)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_create_with_event_organizer(db, client, user, jwt):
    event = get_event(db, user=user)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_create_with_event_user_error(db, client, jwt):
    event = get_event(db)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403

    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def test_create_with_event_rooms_error(db, client, user, jwt):
    room = get_room(db, user=user)
    event = get_event(db, user=user)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "rooms": {"data": [{"id": str(room.id), "type": "microlocation"}]},
                    "event": {"data": {"id": str(event.id), "type": "event"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 422

    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "A valid relationship with either of resources is required: ['rooms', 'event']"
    )


def test_create_with_event_unique_error(db, client, user, jwt):
    event = get_event(db, user=user)
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    stream = VideoStream.query.get(json.loads(response.data)['data']['id'])

    assert stream.event_id == event.id

    response = client.post(
        '/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 409

    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "Video Stream for this event already exists"
    )

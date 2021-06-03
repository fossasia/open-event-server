import json

from app.api.helpers.db import get_or_create
from app.models import event
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from app.models.video_stream import VideoStream
from tests.factories.attendee import AttendeeOrderSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def get_stream(db, user=None, with_event=False, **kwargs):
    stream = VideoStreamFactoryBase(**kwargs)
    if with_event:
        event = EventFactoryBasic()
        stream.event = event
    else:
        room = MicrolocationSubVideoStreamFactory(video_stream=stream)
        event = room.event
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    return stream


def test_edit_stream_admin(db, client, admin_jwt):
    stream = get_stream(db)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_remove_stream_rooms_admin(db, client, admin_jwt):
    stream = get_stream(db)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {"rooms": {"data": []}},
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert stream.rooms == []


def test_edit_stream_rooms_admin(db, client, admin_jwt):
    stream = get_stream(db)
    old_room = stream.rooms[0]
    room = MicrolocationSubVideoStreamFactory(event=old_room.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(old_room.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert len(stream.rooms) == 2


def test_edit_stream_rooms_different_admin_error(db, client, admin_jwt):
    stream = get_stream(db)
    old_room = stream.rooms[0]
    room = MicrolocationSubVideoStreamFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(old_room.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == 'Video Stream can only be created/edited with rooms of a single event'
    )


def test_edit_stream_rooms_diffent_mixed_admin_error(db, client, admin_jwt):
    stream = get_stream(db)
    room = MicrolocationSubVideoStreamFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 403


def test_delete_stream_admin(db, client, admin_jwt):
    stream = get_stream(db)

    response = client.delete(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200

    stream = VideoStream.query.get(stream.id)

    assert stream == None


def test_edit_stream_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_edit_stream_event_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user, with_event=True)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert stream.url == 'https://meet.jit.si'
    assert stream.name == 'Test'
    assert stream.password == '1234'


def test_remove_stream_rooms_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {"rooms": {"data": []}},
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert stream.rooms == []


def test_edit_stream_rooms_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user)
    old_room = stream.rooms[0]
    room = MicrolocationSubVideoStreamFactory(event=old_room.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(old_room.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200

    db.session.refresh(stream)

    assert len(stream.rooms) == 2


def test_edit_stream_rooms_different_organizer_error(db, client, user, jwt):
    stream = get_stream(db, user=user)
    old_room = stream.rooms[0]
    room = MicrolocationSubVideoStreamFactory()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {
                        "data": [
                            {"id": str(room.id), "type": "microlocation"},
                            {"id": str(old_room.id), "type": "microlocation"},
                        ]
                    }
                },
            }
        }
    )

    assert len(stream.rooms) == 1

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == 'Video Stream can only be created/edited with rooms of a single event'
    )


def test_edit_stream_rooms_different_event_organizer_error(db, client, user, jwt):
    stream = get_stream(db, user=user, with_event=True)
    event = EventFactoryBasic()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def test_edit_stream_rooms_event_organizer_error(db, client, user, jwt):
    stream = get_stream(db, user=user)
    room = stream.rooms[0]
    event = EventFactoryBasic()
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "rooms": {"data": [{"id": str(room.id), "type": "microlocation"}]},
                    "event": {"data": {"id": str(event.id), "type": "event"}},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 422
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "A valid relationship with either of resources is required: ['rooms', 'event']"
    )


def test_edit_stream_switch_rooms_event_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user)
    event = stream.rooms[0].event
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            }
        }
    )

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200


def test_delete_stream_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user)

    response = client.delete(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200

    stream = VideoStream.query.get(stream.id)

    assert stream == None


def test_delete_stream_event_organizer(db, client, user, jwt):
    stream = get_stream(db, user=user, with_event=True)

    response = client.delete(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200

    stream = VideoStream.query.get(stream.id)

    assert stream == None


def test_edit_stream_user_error(db, client, jwt):
    stream = get_stream(db)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 404


def test_edit_stream_event_user_error(db, client, jwt):
    stream = get_stream(db, with_event=True)
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 404


def test_edit_stream_user_accessible_error(db, client, user, jwt):
    stream = get_stream(db)
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(
        event=stream.rooms[0].event, order__status='completed', email=email
    )
    db.session.commit()
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def test_edit_stream_event_user_accessible_error(db, client, user, jwt):
    stream = get_stream(db, with_event=True)
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(event=stream.event, order__status='completed', email=email)
    db.session.commit()
    data = json.dumps(
        {
            'data': {
                'id': str(stream.id),
                'type': 'video-stream',
                'attributes': {
                    "url": "https://meet.jit.si",
                    "name": "Test",
                    "password": "1234",
                },
            }
        }
    )

    assert stream.url != 'https://meet.jit.si'
    assert stream.name != 'Test'
    assert stream.password != '1234'

    response = client.patch(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def test_delete_stream_user_accessible_error(db, client, user, jwt):
    stream = get_stream(db)
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(
        event=stream.rooms[0].event, order__status='completed', email=email
    )
    db.session.commit()

    response = client.delete(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )


def test_delete_stream_event_user_accessible_error(db, client, user, jwt):
    stream = get_stream(db, with_event=True)
    email = 'robust@enchilada.com'
    user._email = email
    AttendeeOrderSubFactory(event=stream.event, order__status='completed', email=email)
    db.session.commit()

    response = client.delete(
        f'/v1/video-streams/{stream.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == "You don't have access to the provided event"
    )

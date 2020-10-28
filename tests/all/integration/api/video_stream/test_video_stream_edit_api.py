import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from app.models.video_stream import VideoStream
from tests.factories.attendee import AttendeeOrderSubFactory
from tests.factories.microlocation import MicrolocationSubVideoStreamFactory
from tests.factories.video_stream import VideoStreamFactoryBase


def get_stream(db, user=None, **kwargs):
    stream = VideoStreamFactoryBase(**kwargs)
    room = MicrolocationSubVideoStreamFactory(video_stream=stream)
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=room.event, role=role)
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
        == "You don't have access to the event of provided rooms"
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
        == "You don't have access to the event of provided rooms"
    )

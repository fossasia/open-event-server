import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
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


def test_create_without_room_error(db, client, admin_jwt):
    data = json.dumps(
        {
            'data': {
                'type': 'video-stream',
                'attributes': {"firstname": "Haider"},
                # "relationships": {
                #     "rooms": [{"data": {"id": str(order.id), "type": "order"}}]
                # },
            }
        }
    )

    response = client.post(
        f'/v1/video-streams',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
        data=data,
    )

    assert response.status_code == 422
    assert json.loads(response.data) == ''

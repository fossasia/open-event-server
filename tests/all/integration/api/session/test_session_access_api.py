import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.session import SessionSubFactory
from tests.factories.speaker import SpeakerSubFactory
from tests.factories.user import UserFactory


def get_session(db, user, event_owner=False, **kwargs):
    new_user = UserFactory(is_admin=False, is_verified=False)

    if event_owner:
        owner = user
        creator = new_user
    else:
        owner = new_user
        creator = user
    session = SessionSubFactory(creator_id=creator.id, **kwargs)
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=owner, event=session.event, role=role)
    db.session.commit()

    return session


def test_session_get_pending_organizer(db, client, user, jwt):
    session = get_session(db, user, event_owner=True, state='draft')

    response = client.get(
        f'/v1/sessions/{session.id}', content_type='application/vnd.api+json', headers=jwt
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(session.id)


def test_session_get_pending_admin(db, client, user, admin_jwt):
    session = get_session(db, user, event_owner=True, state='pending')

    response = client.get(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(session.id)


def test_session_get_pending_creator(db, client, user, jwt):
    session = get_session(db, user, state='draft')

    response = client.get(
        f'/v1/sessions/{session.id}', content_type='application/vnd.api+json', headers=jwt
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(session.id)


def test_session_get_pending_speaker(db, client, user, jwt):
    session = get_session(
        db, UserFactory(is_admin=False, is_verified=False), state='pending'
    )
    session.speakers = [SpeakerSubFactory(event=session.event, user=user)]
    db.session.commit()

    response = client.get(
        f'/v1/sessions/{session.id}', content_type='application/vnd.api+json', headers=jwt
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(session.id)


def test_session_get_user(db, client, user):
    session = get_session(db, user)

    response = client.get(
        f'/v1/sessions/{session.id}', content_type='application/vnd.api+json'
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['id'] == str(session.id)


def test_session_get_pending_user_error(db, client, user):
    session = get_session(db, user, state='pending')

    response = client.get(
        f'/v1/sessions/{session.id}', content_type='application/vnd.api+json'
    )

    assert response.status_code == 404

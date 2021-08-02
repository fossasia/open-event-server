import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.session import SessionSubFactory
from tests.factories.speakers_call import SpeakersCallSubFactory
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
    SpeakersCallSubFactory(event=session.event)
    db.session.commit()

    return session


def test_session_edit_locked_fail(db, client, user, jwt):
    session = get_session(db, user, is_locked=True)
    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"title": "Sheesha"},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 403
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Locked sessions cannot be edited",
                'source': {'pointer': '/data/attributes/is-locked'},
                'status': 403,
                'title': 'Access Forbidden',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert session.title == 'example'


def test_session_edit_locked_allow_organizer(db, client, user, jwt):
    session = get_session(db, user, event_owner=True, is_locked=True)
    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"title": "Sheesha"},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.title == 'Sheesha'


def test_session_unlocked_locked_fail(db, client, user, jwt):
    session = get_session(db, user, is_locked=True)
    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"is-locked": False},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 403
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Locked sessions cannot be edited",
                'source': {'pointer': '/data/attributes/is-locked'},
                'status': 403,
                'title': 'Access Forbidden',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert session.is_locked is True


def test_session_unlock_locked_allow_organizer(db, client, user, jwt):
    session = get_session(db, user, event_owner=True, is_locked=True)
    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"is-locked": False},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.is_locked is False

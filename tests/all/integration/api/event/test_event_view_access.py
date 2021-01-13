import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic


def get_event(db, user=None):
    event = EventFactoryBasic(state='draft')
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    return event


def test_event_draft_get_unauthenticated_error(db, client):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
    )

    assert response.status_code == 404


def test_event_draft_get_normal_error(db, client, jwt):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404


def test_event_draft_get_owner(db, client, user, jwt):
    event = get_event(db, user)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200


def test_event_draft_get_admin(db, client, admin_jwt):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200


def test_event_get_user_role(client, db, user, jwt):
    event = get_event(db, user)

    response = client.get(
        f'/v1/events/{event.id}?include=roles.user,roles.role',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    included = json.loads(response.data)['included']
    assert {item['type'] for item in included} == {'users-events-roles', 'user', 'role'}

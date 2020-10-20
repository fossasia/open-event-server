from tests.factories.event import EventFactoryBasic
from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles


def get_event(db, user=None):
    event = EventFactoryBasic()
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    return event


def test_eventdetails_draft_get_unauthenticateduser_error(db, client):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
    )

    assert response.status_code == 404


def test_eventdetails_draft_get_normaluser_error(db, client, jwt):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404


def test_eventdetails_draft_get_owner(db, client, user, jwt):
    event = get_event(db, user)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200


def test_eventdetails_draft_get_admin(db, client, admin_jwt):
    event = get_event(db)

    response = client.get(
        f'/v1/events/{event.id}',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200

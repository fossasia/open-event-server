import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.attendee import AttendeeOrderTicketSubFactory


def get_minimal_attendee(db, user=None, owner=False, event_status='published'):
    attendee = AttendeeOrderTicketSubFactory(
        order__user=user if not owner else None, event__state=event_status
    )
    if owner:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=attendee.event, role=role)
    db.session.commit()

    return attendee


def test_get_attendees_error(db, client, user, jwt, admin_user, admin_jwt):
    get_minimal_attendee(db, user)

    response = client.get('/v1/attendees', content_type='application/vnd.api+json')

    assert response.status_code == 404

    response = client.get(
        '/v1/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    get_minimal_attendee(db, user, owner=True)

    response = client.get(
        '/v1/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

    get_minimal_attendee(db, admin_user, owner=True)

    response = client.get(
        '/v1/attendees',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 404


def test_get_event_attendees_owner(db, client, user, jwt):
    attendee = get_minimal_attendee(db, user, owner=True)

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) == 1


def test_get_draft_event_attendees_owner(db, client, user, jwt):
    attendee = get_minimal_attendee(db, user, owner=True, event_status='draft')

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) == 1


def test_get_event_attendees_admin(db, client, admin_jwt):
    attendee = get_minimal_attendee(db)

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) == 1


def test_get_draft_event_attendees_admin(db, client, admin_jwt):
    attendee = get_minimal_attendee(db, event_status='draft')

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=admin_jwt,
    )

    assert response.status_code == 200
    assert len(json.loads(response.data)['data']) == 1


def test_get_event_attendees_anon_error(db, client):
    attendee = get_minimal_attendee(db)

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
    )

    assert response.status_code == 401

    attendee = get_minimal_attendee(db, event_status='draft')

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
    )

    assert response.status_code == 401


def test_get_event_attendees_user_error(db, client, user, jwt):
    attendee = get_minimal_attendee(db, user)

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 403

    attendee = get_minimal_attendee(db, event_status='draft')

    response = client.get(
        f'/v1/events/{attendee.event_id}/attendees',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 404

import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.role_invite import RoleInvite
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic
from tests.factories.role_invite import RoleInviteSubFactory
from tests.factories.users_events_roles import UsersEventsRolesSubFactory


def test_event_role_delete(db, client, user, jwt):
    uer = UsersEventsRolesSubFactory(user=user)
    RoleInviteSubFactory(
        status='accepted', event=uer.event, email=user.email, role=uer.role
    )
    db.session.commit()

    assert (
        RoleInvite.query.filter_by(
            email=user.email, event=uer.event, role=uer.role
        ).count()
        == 1
    )

    resp = client.get(f'/v1/events/{uer.event_id}/users-events-roles', headers=jwt)

    assert resp.status_code == 200

    resp = client.delete(f'/v1/users-events-roles/{uer.id}', headers=jwt)

    assert resp.status_code == 200
    assert json.loads(resp.data) == {
        'jsonapi': {'version': '1.0'},
        'meta': {'message': 'Object successfully deleted'},
    }

    assert (
        RoleInvite.query.filter_by(
            email=user.email, event=uer.event, role=uer.role
        ).count()
        == 0
    )

    resp = client.get(f'/v1/events/{uer.event_id}/users-events-roles', headers=jwt)

    assert resp.status_code == 403


def test_email_sanitization(db, client, user, jwt):
    event = EventFactoryBasic()
    role_, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=user, event=event, role=role_)
    role, _ = get_or_create(Role, name='organizer', title_name='Organizer')
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'role-invite',
                "attributes": {"email": "test example.org ", "role_name": "organizer"},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}},
                    "role": {"data": {"id": str(role.id), "type": "role"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/role-invites',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert (
        json.loads(response.data)['errors'][0]['detail'] == 'Not a valid email address.'
    )
    assert response.status_code == 422

    data = json.dumps(
        {
            'data': {
                'type': 'role-invite',
                "attributes": {"email": "  test@example.org ", "role_name": "organizer"},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}},
                    "role": {"data": {"id": str(role.id), "type": "role"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/role-invites',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert json.loads(response.data)['data']['attributes']['email'] == 'test@example.org'
    assert response.status_code == 201

    ri = RoleInviteSubFactory(event=event, role=role, email='  test@example.org  ')
    db.session.commit()
    response = client.get(
        f'/v1/role-invites/{ri.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert json.loads(response.data)['data']['attributes']['email'] == 'test@example.org'

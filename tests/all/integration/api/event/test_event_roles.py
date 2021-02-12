import json

from app.models.role_invite import RoleInvite
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

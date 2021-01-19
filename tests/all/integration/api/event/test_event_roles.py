import json

from tests.factories.users_events_roles import UsersEventsRolesSubFactory


def test_event_role_delete(db, client, user, jwt):
    uer = UsersEventsRolesSubFactory(user=user)
    db.session.commit()

    resp = client.delete(f'/v1/users-events-roles/{uer.id}', headers=jwt)

    assert resp.status_code == 200
    assert json.loads(resp.data) == {
        'jsonapi': {'version': '1.0'},
        'meta': {'message': 'Object successfully deleted'},
    }

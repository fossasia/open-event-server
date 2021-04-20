import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from tests.factories.group import GroupSubFactory


def test_group_role_invite(db, client, user, jwt):
    group = GroupSubFactory(user=user)
    role, _ = get_or_create(Role, name='organizer', title_name='Organizer')
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'users-groups-role',
                "attributes": {"email": "test@example.org"},
                "relationships": {
                    "group": {"data": {"id": str(group.id), "type": "group"}},
                    "role": {"data": {"id": str(role.id), "type": "role"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/users-groups-roles',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

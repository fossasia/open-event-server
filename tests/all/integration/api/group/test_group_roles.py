import json

from app.api.helpers.db import get_or_create
from app.api.helpers.permission_manager import has_access
from app.models.role import Role
from app.models.users_groups_role import UsersGroupsRoles
from tests.factories.event import EventFactoryBasic
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


def test_group_role_access(app, db, user, jwt):
    event = EventFactoryBasic()
    with app.test_request_context(headers=jwt):
        assert has_access('is_coorganizer', event_id=event.id) == False

    group = GroupSubFactory(user=user)
    role, _ = get_or_create(Role, name='organizer', title_name='Organizer')
    ugr = UsersGroupsRoles(
        email=user.email,
        user=user,
        group=group,
        role=role,
        accepted=True,
        role_id=role.id,
    )
    event.group_id = group.id
    db.session.commit()

    with app.test_request_context(headers=jwt):
        assert has_access('is_coorganizer', event_id=event.id) == True

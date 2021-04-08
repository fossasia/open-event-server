import json

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic
from tests.factories.group import GroupFactory


def test_group_post_access_allow(db, client, user, jwt):
    user.is_verified = True
    event = EventFactoryBasic()
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=user, event=event, role=role)

    db.session.commit()
    data = json.dumps(
        {
            "data": {
                "type": "group",
                "relationships": {
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp2"},
            }
        }
    )

    response = client.post(
        f'/v1/groups',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )
    assert json.loads(response.data)['data']['attributes']['name'] == "eventgp2"


def test_group_post_access_deny(db, client, user, jwt):
    user.is_verified = True
    event = EventFactoryBasic()
    role, _ = get_or_create(Role, name='moderator', title_name='Moderator')
    UsersEventsRoles(user=user, event=event, role=role)

    db.session.commit()
    data = json.dumps(
        {
            "data": {
                "type": "group",
                "relationships": {
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp2"},
            }
        }
    )

    response = client.post(
        f'/v1/groups',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )
    assert (
        json.loads(response.data)['errors'][0]['detail'] == 'Event owner access required'
    )


def test_group_patch_access_allow(db, client, user, jwt):
    event = EventFactoryBasic()

    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=user, event=event, role=role)

    db.session.commit()

    group = GroupFactory(user_id=user.id)
    db.session.commit()

    data = json.dumps(
        {
            "data": {
                "type": "group",
                "id": str(group.id),
                "relationships": {
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp1"},
            }
        }
    )

    response = client.patch(
        f'/v1/groups/{group.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )
    assert json.loads(response.data)['data']['id'] == str(group.id)


def test_group_patch_access_deny(db, client, user, jwt):
    event = EventFactoryBasic()
    role, _ = get_or_create(Role, name='moderator', title_name='Moderator')
    UsersEventsRoles(user=user, event=event, role=role)
    db.session.commit()

    group = GroupFactory(user_id=user.id)
    db.session.commit()

    data = json.dumps(
        {
            "data": {
                "type": "group",
                "id": str(group.id),
                "relationships": {
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp1"},
            }
        }
    )

    response = client.patch(
        f'/v1/groups/{group.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )
    assert (
        json.loads(response.data)['errors'][0]['detail'] == 'Event owner access required'
    )

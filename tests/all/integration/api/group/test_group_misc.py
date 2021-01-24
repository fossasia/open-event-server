import json

from flask_jwt_extended import create_access_token

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic
from tests.factories.group import GroupFactory
from tests.factories.user import UserFactory


def test_group_post_access_allow(db, client):
    new_user = UserFactory(is_admin=False, is_verified=True)
    event = EventFactoryBasic()
    role, _ = get_or_create(Role, name='coorganizer', title_name='Co-organizer')
    UsersEventsRoles(user=new_user, event=event, role=role)

    db.session.commit()
    data = json.dumps(
        {
            "data": {
                "type": "group",
                "relationships": {
                    "user": {"data": {"id": str(new_user.id), "type": "user"}},
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp2"},
            }
        }
    )

    response = client.post(
        f'/v1/groups',
        content_type='application/vnd.api+json',
        headers={'Authorization': 'JWT ' + create_access_token(new_user.id, fresh=True)},
        data=data,
    )
    assert json.loads(response.data)['data']['attributes']['name'] == "eventgp2"


def test_group_post_access_deny(db, client):
    new_user = UserFactory(is_admin=False, is_verified=True)
    event = EventFactoryBasic()
    role, _ = get_or_create(Role, name='moderator', title_name='Moderator')
    UsersEventsRoles(user=new_user, event=event, role=role)

    db.session.commit()
    data = json.dumps(
        {
            "data": {
                "type": "group",
                "relationships": {
                    "user": {"data": {"id": str(new_user.id), "type": "user"}},
                    "events": {"data": [{"id": str(event.id), "type": "event"}]},
                },
                "attributes": {"name": "eventgp2"},
            }
        }
    )

    response = client.post(
        f'/v1/groups',
        content_type='application/vnd.api+json',
        headers={'Authorization': 'JWT ' + create_access_token(new_user.id, fresh=True)},
        data=data,
    )
    assert (
        json.loads(response.data)['errors'][0]['detail']
        == 'Event co-organizer access required'
    )


def test_group_patch_access_allow(db, client, user, jwt):
    event = EventFactoryBasic()

    role, _ = get_or_create(Role, name='coorganizer', title_name='Coorganizer')
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
                    "user": {"data": {"id": str(user.id), "type": "user"}},
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
                    "user": {"data": {"id": str(user.id), "type": "user"}},
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
        json.loads(response.data)['errors'][0]['detail']
        == 'Event co-organizer access required'
    )

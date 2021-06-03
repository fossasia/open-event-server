import json

from app.api.helpers.db import get_or_create
from app.models.custom_form import CustomForms
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic
from tests.factories.speaker import SpeakerSubFactory
from tests.factories.speakers_call import SpeakersCallSubFactory


def get_event(db, user=None):
    event = EventFactoryBasic(state='published')
    if user:
        role, _ = get_or_create(Role, name='owner', title_name='Owner')
        UsersEventsRoles(user=user, event=event, role=role)
    CustomForms(
        event=event,
        form='speaker',
        field_identifier='email',
        type='text',
        is_included=True,
        is_required=True,
    )
    db.session.commit()

    return event


def test_create_speaker_without_email(db, client, user, jwt):
    event = get_event(db)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb Jamal"},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            },
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    assert json.loads(response.data)['data']['attributes']['email'] == user._email

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb Jamal", "is-email-overridden": True},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            },
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Organizer access required to override email",
                'source': {'pointer': '/data/attributes/is_email_overridden'},
                'status': 403,
                'title': 'Access Forbidden',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


def test_create_speaker_email_override(db, client, user, jwt):
    event = get_event(db, user)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb Jamal"},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            },
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    assert json.loads(response.data)['data']['attributes']['email'] == user.email

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb Jamal", "is-email-overridden": True},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            },
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    assert json.loads(response.data)['data']['attributes']['email'] is None

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb Jamal", "email": "abc@def.org"},
                "relationships": {
                    "event": {"data": {"id": str(event.id), "type": "event"}}
                },
            },
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201
    assert json.loads(response.data)['data']['attributes']['email'] == "abc@def.org"


def get_minimal_speaker(db, user, organizer=False):
    speaker = SpeakerSubFactory(
        gender=None,
        mobile=None,
        organisation=None,
        position=None,
        short_biography=None,
        speaking_experience=None,
        city=None,
        heard_from=None,
        email=user.email,
        user=user,
        event=get_event(db, user if organizer else None),
    )
    SpeakersCallSubFactory(event=speaker.event)
    db.session.commit()

    return speaker


def test_edit_speaker_email_required(db, client, user, jwt):
    speaker = get_minimal_speaker(db, user)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "id": str(speaker.id),
                "attributes": {"name": "Areeb Jamal", "email": None},
            },
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['email'] == user._email

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "id": str(speaker.id),
                "attributes": {"name": "Areeb Jamal", "is-email-overridden": True},
            },
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 403
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Organizer access required to override email",
                'source': {'pointer': '/data/attributes/is_email_overridden'},
                'status': 403,
                'title': 'Access Forbidden',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "id": str(speaker.id),
                "attributes": {"name": "Areeb Jamal", "email": "abc@def.org"},
            },
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['email'] == user._email


def test_edit_speaker_email_override(db, client, user, jwt):
    speaker = get_minimal_speaker(db, user, organizer=True)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "id": str(speaker.id),
                "attributes": {"name": "Areeb Jamal", "email": None},
            },
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['email'] == user.email

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "id": str(speaker.id),
                "attributes": {"name": "Areeb Jamal", "is-email-overridden": True},
            },
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 200
    assert json.loads(response.data)['data']['attributes']['email'] is None

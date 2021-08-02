import json

from app.models.custom_form import CustomForms
from app.models.speaker import Speaker
from tests.factories.speaker import SpeakerSubFactory
from tests.factories.speakers_call import SpeakersCallSubFactory


def get_minimal_speaker(db, user=None):
    speaker = SpeakerSubFactory(
        gender=None,
        mobile=None,
        organisation=None,
        position=None,
        short_biography=None,
        speaking_experience=None,
        city=None,
        heard_from=None,
        email=user and user._email,
        user=user,
        event__state='published',
    )
    SpeakersCallSubFactory(event=speaker.event)
    db.session.commit()

    return speaker


def test_edit_speaker_minimum_fields(db, client, user, jwt):
    speaker = get_minimal_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {"name": "Areeb Jamal"},
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 200
    assert speaker.name == 'Areeb Jamal'


def get_simple_custom_form_speaker(db, user=None):
    speaker = get_minimal_speaker(db, user)
    CustomForms(
        event=speaker.event,
        form='speaker',
        field_identifier='mobile',
        type='number',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=speaker.event,
        form='speaker',
        field_identifier='speakingExperience',
        type='text',
        is_included=True,
        is_required=True,
    )
    db.session.commit()

    return speaker


def test_edit_speaker_required_fields_missing(db, client, user, jwt):
    speaker = get_simple_custom_form_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {
                    "name": "Areeb",
                    "city": "hello@world.com",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['mobile', 'speaking_experience']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert speaker.name != 'Areeb'
    assert speaker.city is None


def test_create_speaker_required_fields_missing(db, client, jwt):
    speaker = get_simple_custom_form_speaker(db)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {
                    "name": "Areeb",
                    "city": "hello@world.com",
                },
                "relationships": {
                    "event": {"data": {"id": str(speaker.event_id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['mobile', 'speaking_experience']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


def test_edit_speaker_required_fields_complete(db, client, user, jwt):
    speaker = get_simple_custom_form_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {
                    "name": "Areeb",
                    "mobile": "456345678",
                    "speaking-experience": "Speaking since birth",
                    "complex-field-values": {
                        "m.night": "shyamalan"
                    },  # Should be ignored and saved as None
                },
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 200

    assert speaker.name == 'Areeb'
    assert speaker.mobile == '456345678'
    assert speaker.complex_field_values is None


def test_create_speaker_required_fields_complete(db, client, jwt):
    speaker = get_simple_custom_form_speaker(db)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {
                    "name": "Areeb",
                    "mobile": "456345678",
                    "speaking-experience": "Speaking since birth",
                    "complex-field-values": {
                        "m.night": "shyamalan"
                    },  # Should be ignored and saved as None
                },
                "relationships": {
                    "event": {"data": {"id": str(speaker.event_id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    speaker = Speaker.query.get(json.loads(response.data)['data']['id'])

    assert speaker.name == 'Areeb'
    assert speaker.mobile == '456345678'
    assert speaker.complex_field_values is None


def get_complex_custom_form_speaker(db, user=None):
    speaker = get_minimal_speaker(db, user)
    CustomForms(
        event=speaker.event,
        form='speaker',
        field_identifier='heardFrom',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=speaker.event,
        form='speaker',
        field_identifier='bestFriend',
        name='Best Friend',
        type='text',
        is_included=True,
        is_required=True,
        is_complex=True,
    )
    CustomForms(
        event=speaker.event,
        form='speaker',
        field_identifier='transFatContent',
        name='Trans Fat Content',
        type='number',
        is_included=True,
        is_required=False,
        is_complex=True,
    )
    db.session.commit()

    return speaker


def test_custom_form_complex_fields_missing_required(db, client, user, jwt):
    speaker = get_complex_custom_form_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {"name": "Areeb"},
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['best_friend', 'heard_from']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert speaker.name != 'Areeb'
    assert speaker.complex_field_values is None


def test_custom_form_create_complex_fields_missing_required(db, client, jwt):
    speaker = get_complex_custom_form_speaker(db)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {"name": "Areeb"},
                "relationships": {
                    "event": {"data": {"id": str(speaker.event_id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['best_friend', 'heard_from']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert speaker.name != 'Areeb'
    assert speaker.complex_field_values is None


def test_custom_form_complex_fields_complete(db, client, user, jwt):
    speaker = get_complex_custom_form_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {
                    "name": "Areeb",
                    "heard-from": "Gypsie",
                    "complex-field-values": {"best-friend": "Tester"},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 200

    assert speaker.name == 'Areeb'
    assert speaker.heard_from == 'Gypsie'
    assert speaker.complex_field_values['best_friend'] == 'Tester'


def test_custom_form_create_complex_fields_complete(db, client, jwt):
    speaker = get_complex_custom_form_speaker(db)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                "attributes": {
                    "name": "Areeb",
                    "heard-from": "Gypsie",
                    "complex-field-values": {"best-friend": "Tester"},
                },
                "relationships": {
                    "event": {"data": {"id": str(speaker.event_id), "type": "event"}}
                },
            }
        }
    )

    response = client.post(
        '/v1/speakers',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    speaker = Speaker.query.get(json.loads(response.data)['data']['id'])

    assert response.status_code == 201

    assert speaker.name == 'Areeb'
    assert speaker.heard_from == 'Gypsie'
    assert speaker.complex_field_values['best_friend'] == 'Tester'


def test_ignore_complex_custom_form_fields(db, client, user, jwt):
    """Test to see that extra data from complex JSON is dropped"""
    speaker = get_complex_custom_form_speaker(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'speaker',
                'id': str(speaker.id),
                "attributes": {
                    "name": "Areeb",
                    "heard-from": "Gypsie",
                    "complex-field-values": {
                        "bestFriend": "Bester",
                        "transFat-content": 20.08,
                        "shalimar": "sophie",
                    },
                },
            }
        }
    )

    response = client.patch(
        f'/v1/speakers/{speaker.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(speaker)

    assert response.status_code == 200

    assert speaker.name == 'Areeb'
    assert speaker.heard_from == 'Gypsie'
    assert speaker.complex_field_values['best_friend'] == 'Bester'
    assert speaker.complex_field_values['trans_fat_content'] == 20.08
    assert speaker.complex_field_values.get('shalimar') is None

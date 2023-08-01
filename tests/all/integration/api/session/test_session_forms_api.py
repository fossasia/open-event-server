import json

from app.models.custom_form import CustomForms
from app.models.session import Session
from tests.factories.session import SessionSubFactory
from tests.factories.speakers_call import SpeakersCallSubFactory
from tests.factories.track import TrackSubFactory


def get_minimal_session(db, user):
    session = SessionSubFactory(
        subtitle=None,
        level=None,
        language=None,
        short_abstract=None,
        slides_url=None,
        state=None,
        is_locked=False,
        creator_id=user.id,
    )
    SpeakersCallSubFactory(event=session.event)
    db.session.commit()

    return session


def test_edit_session_minimum_fields(db, client, user, jwt):
    session = get_minimal_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Kubernetes",
                    "subtitle": "The needlessly complicated orchestration platform",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.title == 'Kubernetes'
    assert session.subtitle == 'The needlessly complicated orchestration platform'


def get_simple_custom_form_session(db, user):
    session = get_minimal_session(db, user)
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='track',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='level',
        type='number',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='shortAbstract',
        type='text',
        is_included=True,
        is_required=True,
    )
    db.session.commit()

    return session


def test_edit_session_required_fields_missing(db, client, user, jwt):
    session = get_simple_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "language": "English",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['Level', 'Short Abstract']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert session.title != 'Move Away'
    assert session.subtitle != 'Moooove'
    assert session.language is None


def test_create_session_required_fields_missing(db, client, user, jwt):
    session = get_simple_custom_form_session(db, user)
    track = TrackSubFactory(event=session.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "language": "English",
                },
                "relationships": {
                    "event": {"data": {"id": str(session.event_id), "type": "event"}},
                    "track": {"data": {"id": str(track.id), "type": "track"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/sessions',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['Level', 'Short Abstract']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }


def test_edit_session_required_fields_complete(db, client, user, jwt):
    session = get_simple_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "level": "Expert",
                    "short-abstract": "Speaking since birth",
                    "complex-field-values": {
                        "bojack": "horseman"
                    },  # Should be ignored and saved as None
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200

    assert session.title == 'Move Away'
    assert session.subtitle == 'Moooove'
    assert session.level == 'Expert'
    assert session.short_abstract == 'Speaking since birth'
    assert session.complex_field_values is None


def test_create_session_required_fields_complete(db, client, user, jwt):
    session = get_simple_custom_form_session(db, user)
    track = TrackSubFactory(event=session.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "level": "Expert",
                    "short-abstract": "Speaking since birth",
                    "complex-field-values": {
                        "bojack": "horseman"
                    },  # Should be ignored and saved as None
                },
                "relationships": {
                    "event": {"data": {"id": str(session.event_id), "type": "event"}},
                    "track": {"data": {"id": str(track.id), "type": "track"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/sessions',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    assert response.status_code == 201

    session = Session.query.get(json.loads(response.data)['data']['id'])

    assert session.title == 'Move Away'
    assert session.subtitle == 'Moooove'
    assert session.level == 'Expert'
    assert session.short_abstract == 'Speaking since birth'
    assert session.complex_field_values is None


def get_complex_custom_form_session(db, user):
    session = get_minimal_session(db, user)
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='track',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='slidesUrl',
        type='text',
        is_included=True,
        is_required=True,
    )
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='bestFriend',
        name='Best Friend',
        type='text',
        is_included=True,
        is_required=True,
        is_complex=True,
    )
    CustomForms(
        event=session.event,
        form='session',
        field_identifier='transFatContent',
        name='Trans Fat Content',
        type='number',
        is_included=True,
        is_required=False,
        is_complex=True,
    )
    db.session.commit()

    return session


def test_custom_form_complex_fields_missing_required(db, client, user, jwt):
    session = get_complex_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "language": "English",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['Best Friend', 'Slide']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert session.title != 'Move Away'
    assert session.subtitle != 'Moooove'
    assert session.language is None


def test_custom_form_create_complex_fields_missing_required(db, client, user, jwt):
    session = get_complex_custom_form_session(db, user)
    track = TrackSubFactory(event=session.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "language": "English",
                },
                "relationships": {
                    "event": {"data": {"id": str(session.event_id), "type": "event"}},
                    "track": {"data": {"id": str(track.id), "type": "track"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/sessions',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['Best Friend', 'Slide']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

    assert session.title != 'Move Away'
    assert session.subtitle != 'Moooove'
    assert session.language is None


def test_custom_form_complex_fields_complete(db, client, user, jwt):
    session = get_complex_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "slides-url": "http://gypsie.com",
                    "complex-field-values": {"best-friend": "Tester"},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200

    assert session.title == 'Move Away'
    assert session.subtitle == 'Moooove'
    assert session.slides_url == 'http://gypsie.com'
    assert session.complex_field_values['best_friend'] == 'Tester'


def test_custom_form_create_complex_fields_complete(db, client, user, jwt):
    session = get_complex_custom_form_session(db, user)
    track = TrackSubFactory(event=session.event)
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "slides-url": "http://gypsie.com",
                    "complex-field-values": {"best-friend": "Tester"},
                },
                "relationships": {
                    "event": {"data": {"id": str(session.event_id), "type": "event"}},
                    "track": {"data": {"id": str(track.id), "type": "track"}},
                },
            }
        }
    )

    response = client.post(
        '/v1/sessions',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    session = Session.query.get(json.loads(response.data)['data']['id'])

    assert response.status_code == 201

    assert session.title == 'Move Away'
    assert session.subtitle == 'Moooove'
    assert session.slides_url == 'http://gypsie.com'
    assert session.complex_field_values['best_friend'] == 'Tester'


def test_ignore_complex_custom_form_fields(db, client, user, jwt):
    """Test to see that extra data from complex JSON is dropped"""
    session = get_complex_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "title": "Move Away",
                    "subtitle": "Moooove",
                    "slides-url": "http://gypsie.com",
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
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200

    assert session.title == 'Move Away'
    assert session.subtitle == 'Moooove'
    assert session.slides_url == 'http://gypsie.com'
    assert session.complex_field_values['best_friend'] == 'Bester'
    assert session.complex_field_values['trans_fat_content'] == 20.08
    assert session.complex_field_values.get('shalimar') is None


def test_edit_session_only_state(db, client, user, jwt):
    # Should be allowed for organizers
    user.is_admin = True
    session = get_simple_custom_form_session(db, user)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "state": "withdrawn",
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.state == 'withdrawn'


def test_edit_session_custom_allow(db, client, user, jwt):
    """If there already is some complex field value of session,
    and we don't send any new value, then it shouldn't be validated"""
    user.is_admin = True
    session = get_simple_custom_form_session(db, user)
    session.complex_field_values = {'test': 'hello'}
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"state": "withdrawn"},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.state == 'withdrawn'
    assert session.complex_field_values == {'test': 'hello'}


def test_edit_session_custom_same_allow(db, client, user, jwt):
    """If there already is some complex field value of session,
    and we don't send any new value, then it shouldn't be validated"""
    user.is_admin = True
    session = get_simple_custom_form_session(db, user)
    session.complex_field_values = {'test': 'hello'}
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {
                    "state": "withdrawn",
                    "complex-field-values": {'test': 'hello'},
                },
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 200
    assert session.state == 'withdrawn'
    assert session.complex_field_values == {'test': 'hello'}


def test_edit_session_custom_none_disallow(db, client, user, jwt):
    """If there already is some complex field value of session,
    and we send any null value, then it shouldn't be allowed"""
    user.is_admin = True
    session = get_simple_custom_form_session(db, user)
    session.complex_field_values = {'test': 'hello'}
    db.session.commit()

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"state": "withdrawn", "complex_field_values": None},
            }
        }
    )

    response = client.patch(
        f'/v1/sessions/{session.id}',
        content_type='application/vnd.api+json',
        headers=jwt,
        data=data,
    )

    db.session.refresh(session)

    assert response.status_code == 422
    assert session.complex_field_values == {'test': 'hello'}

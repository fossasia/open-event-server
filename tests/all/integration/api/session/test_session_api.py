import json

from app.models.custom_form import CustomForms
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
                'detail': "Missing required fields ['level', 'short_abstract']",
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
        '/v1/sessions', content_type='application/vnd.api+json', headers=jwt, data=data,
    )

    # assert response.status_code == 422
    assert json.loads(response.data) == {
        'errors': [
            {
                'detail': "Missing required fields ['level', 'short_abstract']",
                'source': {'pointer': '/data/attributes'},
                'status': 422,
                'title': 'Unprocessable Entity',
            }
        ],
        'jsonapi': {'version': '1.0'},
    }

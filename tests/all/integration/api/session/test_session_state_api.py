import json

import pytest

from app.api.helpers.db import get_or_create
from app.models.role import Role
from app.models.users_events_role import UsersEventsRoles
from tests.factories.session import SessionSubFactory
from tests.factories.speakers_call import SpeakersCallSubFactory
from tests.factories.user import UserFactory


def get_session(db, user, event_owner=True, **kwargs):
    new_user = UserFactory(is_admin=False, is_verified=False)

    if event_owner:
        owner = user
        creator = new_user
    else:
        owner = new_user
        creator = user
    session = SessionSubFactory(creator_id=creator.id, **kwargs)
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=owner, event=session.event, role=role)
    SpeakersCallSubFactory(event=session.event)
    db.session.commit()

    return session


# TODO(Areeb): Remove some states from tests to reduce testing time.
# Not every state change needs to be tested
def _test_state_change(
    db, client, user, jwt, new_state, state, event_owner=True, error=True
):
    session = get_session(db, user, event_owner=event_owner, state=state)

    data = json.dumps(
        {
            'data': {
                'type': 'session',
                'id': str(session.id),
                "attributes": {"state": new_state},
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

    if error:
        assert response.status_code == 403
        assert json.loads(response.data) == {
            'errors': [
                {
                    'detail': f'You cannot change a session state from "{state}" to "{new_state}"',
                    'source': {'pointer': '/data/attributes/state'},
                    'status': 403,
                    'title': 'Access Forbidden',
                }
            ],
            'jsonapi': {'version': '1.0'},
        }

        assert session.state == state
    else:
        assert response.status_code == 200
        assert session.state == new_state


@pytest.mark.parametrize('new_state', ['accepted', 'confirmed', 'rejected'])
def test_draft_organizer_error(db, client, user, jwt, new_state, state='draft'):
    _test_state_change(db, client, user, jwt, new_state, state=state)


def _create_permutations(statesA, statesB):
    results = []
    for stateA in statesA:
        for stateB in statesB:
            results.append((stateA, stateB))
    return results


states = _create_permutations(
    ['draft', 'pending', 'accepted', 'confirmed', 'rejected'],
    ['accepted', 'confirmed', 'rejected', 'canceled'],
)


@pytest.mark.parametrize('state,new_state', states)
def test_draft_speaker_error(db, client, user, jwt, new_state, state):
    if state == new_state:
        return
    _test_state_change(db, client, user, jwt, new_state, state=state, event_owner=False)


@pytest.mark.parametrize('new_state', ['pending'])
def test_draft_speaker_allow(db, client, user, jwt, new_state, state='draft'):
    _test_state_change(
        db, client, user, jwt, new_state, state=state, event_owner=False, error=False
    )


states = _create_permutations(
    ['pending', 'accepted', 'confirmed', 'rejected', 'canceled'], ['withdrawn']
)


@pytest.mark.parametrize('state,new_state', states)
def test_withdraw_speaker_allow(db, client, user, jwt, new_state, state):
    _test_state_change(
        db, client, user, jwt, new_state, state=state, event_owner=False, error=False
    )


states = _create_permutations(['withdrawn'], ['pending'])


def test_withdraw_speaker_error(
    db, client, user, jwt, new_state='withdrawn', state='draft'
):
    _test_state_change(db, client, user, jwt, new_state, state=state, event_owner=False)


states = _create_permutations(
    ['pending', 'accepted', 'confirmed', 'rejected', 'canceled'], ['withdrawn']
)


@pytest.mark.parametrize('state,new_state', states)
def test_withdraw_organizer_allow(db, client, user, jwt, new_state, state):
    _test_state_change(db, client, user, jwt, new_state, state=state, error=False)


states = _create_permutations(['withdrawn'], ['accepted', 'confirmed', 'rejected'])

states = _create_permutations(['pending'], ['accepted', 'confirmed', 'rejected'])


@pytest.mark.parametrize('state,new_state', states)
def test_pending_organizer_allow(db, client, user, jwt, new_state, state):
    _test_state_change(db, client, user, jwt, new_state, state=state, error=False)


states = _create_permutations(['rejected'], ['accepted', 'confirmed'])


@pytest.mark.parametrize('state,new_state', states)
def test_revert_rejected_organizer_allow(db, client, user, jwt, new_state, state):
    _test_state_change(db, client, user, jwt, new_state, state=state, error=False)


states = _create_permutations(['accepted', 'confirmed'], ['canceled'])


@pytest.mark.parametrize('state,new_state', states)
def test_canceled_organizer_allow(db, client, user, jwt, new_state, state):
    _test_state_change(db, client, user, jwt, new_state, state=state, error=False)


states = _create_permutations(['pending', 'rejected', 'withdrawn'], ['canceled'])


def test_confirmed_organizer_allow(
    db, client, user, jwt, new_state='canceled', state='confirmed'
):
    _test_state_change(db, client, user, jwt, new_state, state=state, error=False)

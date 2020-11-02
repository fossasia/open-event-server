import pytest
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.db import get_or_create
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.query import event_query
from app.models.event import Event
from app.models.order import Order
from app.models.role import Role
from app.models.ticket import Ticket
from app.models.users_events_role import UsersEventsRoles
from tests.factories.event import EventFactoryBasic


def test_query_no_op(client):
    query = Order.query
    assert event_query(query, {}) == query


@pytest.fixture
def event(db):
    return EventFactoryBasic(id=123, identifier='ashgdas6d3', state='published')


def test_query_event(event):
    assert str(event_query(Order.query, {'event_id': event.id})) == str(
        Order.query.join(Event).filter(Event.id == event.id)
    )
    assert str(event_query(Ticket.query, {'event_identifier': event.identifier})) == str(
        Ticket.query.join(Event).filter(Event.id == event.id)
    )


def test_query_no_event(client):
    with pytest.raises(ObjectNotFound):
        event_query(Order.query, {'event_id': 123})


def test_query_draft_event_error(event):
    event.state = 'draft'
    with pytest.raises(ObjectNotFound):
        event_query(Ticket.query, {'event_id': event.id})
    with pytest.raises(ObjectNotFound):
        event_query(Order.query, {'event_identifier': event.identifier})


def test_query_draft_event_user_error(event, user_login):
    "Different user should not be able to access draft event of other user"
    event.state = 'draft'
    with pytest.raises(ObjectNotFound):
        event_query(Ticket.query, {'event_id': event.id})
    with pytest.raises(ObjectNotFound):
        event_query(Order.query, {'event_identifier': event.identifier})


def get_owner(event, user):
    role, _ = get_or_create(Role, name='owner', title_name='Owner')
    UsersEventsRoles(user=user, event=event, role=role)
    return user


def test_query_draft_event_organizer(event, user, user_login):
    get_owner(event, user)
    event.state = 'draft'

    assert str(event_query(Order.query, {'event_id': event.id})) == str(
        Order.query.join(Event).filter(Event.id == event.id)
    )
    assert str(event_query(Ticket.query, {'event_identifier': event.identifier})) == str(
        Ticket.query.join(Event).filter(Event.id == event.id)
    )


def test_query_draft_event_admin(event, admin_login):
    event.state = 'draft'

    assert str(event_query(Order.query, {'event_id': event.id})) == str(
        Order.query.join(Event).filter(Event.id == event.id)
    )
    assert str(event_query(Ticket.query, {'event_identifier': event.identifier})) == str(
        Ticket.query.join(Event).filter(Event.id == event.id)
    )


def test_query_restricted_event_error(event):
    with pytest.raises(ForbiddenError):
        event_query(Ticket.query, {'event_id': event.id}, restrict=True)
    with pytest.raises(ForbiddenError):
        event_query(Order.query, {'event_identifier': event.identifier}, restrict=True)


def test_query_restricted_event_user_error(event, user_login):
    with pytest.raises(ForbiddenError):
        event_query(Ticket.query, {'event_id': event.id}, restrict=True)
    with pytest.raises(ForbiddenError):
        event_query(Order.query, {'event_identifier': event.identifier}, restrict=True)


def test_query_restricted_event_organizer(event, user, user_login):
    get_owner(event, user)

    assert str(event_query(Order.query, {'event_id': event.id}, restrict=True)) == str(
        Order.query.join(Event).filter(Event.id == event.id)
    )
    assert str(
        event_query(Ticket.query, {'event_identifier': event.identifier}, restrict=True)
    ) == str(Ticket.query.join(Event).filter(Event.id == event.id))


def test_query_restricted_event_admin(event, admin_login):

    assert str(event_query(Order.query, {'event_id': event.id}, restrict=True)) == str(
        Order.query.join(Event).filter(Event.id == event.id)
    )
    assert str(
        event_query(Ticket.query, {'event_identifier': event.identifier}, restrict=True)
    ) == str(Ticket.query.join(Event).filter(Event.id == event.id))

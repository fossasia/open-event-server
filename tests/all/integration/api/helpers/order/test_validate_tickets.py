from datetime import datetime

import pytest
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.ticketing import validate_tickets
from tests.factories.event import EventFactoryBasic
from tests.factories.ticket import TicketSubFactory


def test_validate_empty_tickets():
    assert validate_tickets([]) == []


def test_validate_tickets(db):
    tickets = TicketSubFactory.create_batch(3, event=EventFactoryBasic())
    db.session.commit()

    assert validate_tickets([str(ticket.id) for ticket in tickets]) == tickets


def test_reject_tickets_of_different_events(db):
    tickets = TicketSubFactory.create_batch(3)
    db.session.commit()

    with pytest.raises(
        UnprocessableEntityError,
        match=r'All tickets must belong to same event. Found: .*',
    ):
        validate_tickets([ticket.id for ticket in tickets])


def test_reject_deleted_tickets(db):
    event = EventFactoryBasic()
    tickets = TicketSubFactory.create_batch(3, event=event)
    tickets.append(TicketSubFactory(deleted_at=datetime.now(), event=event))
    db.session.commit()

    with pytest.raises(ObjectNotFound, match=r'Tickets not found for IDs: .*'):
        validate_tickets([ticket.id for ticket in tickets])

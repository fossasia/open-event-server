from datetime import datetime

import pytest

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.ticketing import validate_discount_code
from tests.factories.attendee import AttendeeSubFactory
from tests.factories.discount_code import DiscountCodeTicketSubFactory
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderSubFactory
from tests.factories.ticket import TicketSubFactory


def _create_discount_code(db, **kwargs):
    tickets = TicketSubFactory.create_batch(3, event=EventFactoryBasic(), **kwargs)
    discount = DiscountCodeTicketSubFactory(tickets_number=5, tickets=tickets)
    db.session.commit()

    return discount, [{'id': ticket.id} for ticket in tickets]


def test_validate_discount_code(db):
    discount, tickets = _create_discount_code(db)

    assert discount.validate(tickets=tickets) == discount


def test_validate_discount_code_id(db):
    discount, tickets = _create_discount_code(db)

    assert validate_discount_code(discount.id, tickets=tickets) == discount
    assert validate_discount_code(str(discount.id), tickets=tickets) == discount


def test_validate_discount_code_require_tickets_or_holders(db):
    with pytest.raises(ValueError):
        DiscountCodeTicketSubFactory(tickets=[]).validate()


def test_validate_discount_code_require_same_event_id(db):
    discount, tickets = _create_discount_code(db)
    discount.event = EventFactoryBasic()
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(event_id='40', tickets=tickets)

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(event_id=100, tickets=tickets)

    assert discount.validate(event_id=discount.event_id, tickets=tickets) == discount


def test_validate_discount_code_reject_deleted_tickets(db):
    discount, _ = _create_discount_code(db)
    deleted_tickets = TicketSubFactory.create_batch(2, deleted_at=datetime.now())
    discount.tickets += deleted_tickets
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(tickets=[{'id': ticket.id} for ticket in deleted_tickets])


def test_validate_discount_code_accept_mix_deleted_tickets(db):
    discount, tickets = _create_discount_code(db)
    deleted_tickets = TicketSubFactory.create_batch(2, deleted_at=datetime.now())
    discount.tickets += deleted_tickets
    db.session.commit()

    assert (
        discount.validate(
            tickets=tickets + [{'id': ticket.id} for ticket in deleted_tickets]
        )
        == discount
    )


def test_validate_discount_code_reject_inactive(db):
    discount, tickets = _create_discount_code(db)
    discount.is_active = False
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(tickets=tickets)


def test_validate_discount_code_reject_expired(db):
    discount, tickets = _create_discount_code(db)
    discount.valid_till = datetime(2014, 1, 1)
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(tickets=tickets)


def test_validate_discount_code_reject_future(db):
    discount, tickets = _create_discount_code(db)
    discount.valid_from = datetime(2099, 1, 1)
    db.session.commit()

    with pytest.raises(UnprocessableEntityError, match='Invalid Discount Code'):
        discount.validate(tickets=tickets)


def _create_discounted_attendees(db):
    discount, tickets = _create_discount_code(db)
    order_with_discount = OrderSubFactory(status='completed', discount_code=discount)
    AttendeeSubFactory.create_batch(
        3, order=order_with_discount, ticket_id=tickets[0]['id']
    )
    db.session.commit()

    return discount, tickets


# def test_validate_discount_code_reject_exhausted(db):
#     discount, tickets = _create_discounted_attendees(db)

#     with pytest.raises(UnprocessableEntityError, match='Discount Usage Exceeded'):
#         discount.validate(tickets=tickets[:3])


def test_validate_discount_code_accept_available(db):
    discount, tickets = _create_discounted_attendees(db)

    assert discount.validate(tickets=tickets[:2]) == discount

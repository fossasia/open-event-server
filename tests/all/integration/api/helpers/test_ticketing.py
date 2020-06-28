from tests.factories.attendee import AttendeeFactoryBase
from tests.factories.discount_code import DiscountCodeTicketFactory
from tests.factories.order import OrderFactory
from tests.factories.ticket import TicketSubFactory


def test_match_discount_quantity(db):
    """Method to test the quantity calculation of discount code"""

    ticket = TicketSubFactory()
    discount_code = DiscountCodeTicketFactory(tickets_number=5)
    discount_code.tickets.append(ticket)

    order_without_discount = OrderFactory(status='completed')

    db.session.commit()

    # Attendees associated with the order without discount code should not be counted
    AttendeeFactoryBase.create_batch(
        10,
        order_id=order_without_discount.id,
        ticket_id=ticket.id,
        event_id=ticket.event_id,
    )

    assert discount_code.is_available(ticket_holders=[1]) is True

    order_with_discount = OrderFactory(
        status='completed', discount_code_id=discount_code.id
    )

    db.session.commit()

    # Attendees associated with the order with discount code should be counted
    AttendeeFactoryBase.create_batch(
        5, order_id=order_with_discount.id, ticket_id=ticket.id, event_id=ticket.event_id
    )

    assert discount_code.is_available(ticket_holders=[1]) is False
    assert discount_code.confirmed_attendees_count == 5

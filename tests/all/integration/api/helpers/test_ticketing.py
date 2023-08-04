from app.api.helpers.errors import UnprocessableEntityError
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
    quantity_discount: dict = {
        'numb_no_discount': 0,
        'numb_discount': 1,
    }

    discount_quantity = discount_code.is_available(ticket_holders=[1])
    assert discount_quantity.get('numb_discount') == quantity_discount.get(
        'numb_discount'
    )

    order_with_discount = OrderFactory(
        status='completed', discount_code_id=discount_code.id
    )

    db.session.commit()

    # Attendees associated with the order with discount code should be counted
    AttendeeFactoryBase.create_batch(
        5,
        order_id=order_with_discount.id,
        ticket_id=ticket.id,
        event_id=ticket.event_id,
        is_discount_applied=True,
    )

    try:
        discount_code.is_available(ticket_holders=[1])
    except UnprocessableEntityError as e:
        assert e.source['pointer'] == 'discount_sold_out'

    assert discount_code.confirmed_attendees_count == 5

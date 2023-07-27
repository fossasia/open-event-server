from tests.factories.attendee import AttendeeFactoryBase
from tests.factories.event import EventFactoryBasic
from tests.factories.order import OrderFactory
from tests.factories.ticket import TicketFactory


def test_event_search_attendee(db, jwt, client):
    """Method to test the count query of sold tickets"""
    event = EventFactoryBasic()
    ticket = TicketFactory()
    completed_order = OrderFactory(status='completed')

    db.session.commit()

    # will be counted as attendee have valid orders
    AttendeeFactoryBase.create_batch(
        1, order_id=completed_order.id, ticket_id=ticket.id, event_id=event.id
    )

    response = client.get(
        f'/v1/events/{event.id}/attendees/search',
        content_type='application/vnd.api+json',
        headers=jwt,
    )

    assert response.status_code == 200
    assert len(response.json['attendees']) == 1

from app.api.helpers.ticketing import TicketingManager
from app.factories.attendee import AttendeeFactoryBase
from app.factories.order import OrderFactory
from app.factories.ticket import TicketFactory
from app.factories.discount_code import DiscountCodeTicketFactory
from app.models import db

from tests.all.integration.utils import OpenEventTestCase


class TestTicketing(OpenEventTestCase):
    def test_match_discount_quantity(self):
        """Method to test the quantity calculation of discount code"""

        with self.app.test_request_context():
            ticket = TicketFactory()
            discount_code = DiscountCodeTicketFactory(tickets_number=5)
            discount_code.tickets.append(ticket)

            order_without_discount = OrderFactory(status='completed')

            db.session.commit()

            # Attendees associated with the order without discount code should not be counted
            AttendeeFactoryBase.create_batch(
                10, order_id=order_without_discount.id, ticket_id=ticket.id
            )

            self.assertTrue(
                TicketingManager.match_discount_quantity(
                    discount_code, ticket_holders=[1]
                )
            )

            order_with_discount = OrderFactory(
                status='completed', discount_code_id=discount_code.id
            )

            db.session.commit()

            # Attendees associated with the order with discount code should be counted
            AttendeeFactoryBase.create_batch(
                5, order_id=order_with_discount.id, ticket_id=ticket.id
            )

            self.assertFalse(
                TicketingManager.match_discount_quantity(
                    discount_code, ticket_holders=[1]
                )
            )
            self.assertEqual(5, discount_code.confirmed_attendees_count)

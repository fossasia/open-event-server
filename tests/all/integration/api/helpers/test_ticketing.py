import unittest


from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.ticketing import TicketingManager
from app.factories.discount_code import DiscountCodeTicketFactory
from app.factories.ticket import TicketFactory
from app.factories.attendee import AttendeeFactory
from app import current_app as app
from app.api.helpers.db import save_to_db


class TestTicketing(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_get_order_expiry(self):
        """Method to test order expiry time"""

        with app.test_request_context():
            ticketing_manager = TicketingManager()
            self.assertEqual(ticketing_manager.get_order_expiry(), 10)

    def test_match_discount_quantity(self):
        """Method to test discount quantity matching"""

        with app.test_request_context():
            ticketing_manager = TicketingManager()
            test_ticket = TicketFactory()
            test_ticket.name = 'test'
            save_to_db(test_ticket)
            discount_test_code = DiscountCodeTicketFactory()
            save_to_db(discount_test_code)
            discount_test_code.ticket_ids = [test_ticket.id]
            attendee_1 = AttendeeFactory()
            attendee_1.ticket = test_ticket
            save_to_db(attendee_1)
            ticket_holders = [attendee_1.id]
            self.assertEqual(ticketing_manager.match_discount_quantity(discount_test_code, ticket_holders), True)


if __name__ == '__main__':
    unittest.main()

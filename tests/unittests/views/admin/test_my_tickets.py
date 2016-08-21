import unittest
from datetime import datetime

from flask import url_for

from app.helpers.data import save_to_db
from app.helpers.ticketing import TicketingManager
from app import current_app as app
from tests.unittests.views.guest.test_ticketing import create_order
from tests.unittests.views.view_test_case import OpenEventViewTestCase

class TestMySession(OpenEventViewTestCase):

    def test_tickets_overview_page(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            order = TicketingManager.get_order_by_identifier(identifier)
            order.user_id = self.super_admin.id
            order.brand = "Visa"
            order.completed_at = datetime.now()
            order.status = "completed"
            order.last4 = "1234"
            order.exp_month = "12"
            order.exp_year = "2050"
            order.paid_via = "stripe"
            order.payment_mode = "card"
            save_to_db(order)
            response = self.app.get(url_for('my_tickets.display_my_tickets'), follow_redirects=True)
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            self.assertTrue(str(ticket.name) not in response.data, msg=response.data)

if __name__ == '__main__':
    unittest.main()

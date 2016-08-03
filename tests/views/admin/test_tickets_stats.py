import unittest
from datetime import datetime

from flask import url_for

from app.helpers.data import save_to_db
from app.helpers.ticketing import TicketingManager
from app import current_app as app
from tests.views.guest.test_ticketing import create_order
from tests.views.view_test_case import OpenEventViewTestCase

class TestsTicketsStats(OpenEventViewTestCase):

    def prep_order(self):
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
        return order

    def test_tickets_view(self):
        with app.test_request_context():
            order = self.prep_order()
            response = self.app.get(url_for('event_ticket_sales.display_ticket_stats', event_id=order.event_id),
                                    follow_redirects=True)
            self.assertTrue('Completed' in response.data, msg=response.data)

    def test_tickets_orders_view(self):
        with app.test_request_context():
            order = self.prep_order()
            response = self.app.get(url_for('event_ticket_sales.display_orders', event_id=order.event_id),
                                    follow_redirects=True)
            self.assertTrue('test_super_admin@email.com' in response.data, msg=response.data)

    def test_tickets_attendees_view(self):
        with app.test_request_context():
            order = self.prep_order()
            response = self.app.get(url_for('event_ticket_sales.display_attendees', event_id=order.event_id),
                                    follow_redirects=True)
            self.assertTrue('Test Ticket' in response.data, msg=response.data)

if __name__ == '__main__':
    unittest.main()

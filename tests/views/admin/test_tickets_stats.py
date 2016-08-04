import unittest
from datetime import datetime

from bs4 import BeautifulSoup
from flask import url_for

from app.helpers.data import save_to_db
from app.helpers.ticketing import TicketingManager
from app import current_app as app
from tests.views.guest.test_ticketing import get_event_ticket
from tests.views.view_test_case import OpenEventViewTestCase

def create_order(self):
    event, ticket = get_event_ticket()
    data = {
        "event_id": event.id,
        "ticket_ids[]": [ticket.id],
        "ticket_quantities[]": [5],
        "ticket_subtotals[]": [str(ticket.price * 5)],
        "payment_via": "stripe"
    }
    response = self.app.post(url_for('event_ticket_sales.add_order', event_id=event.id),
                             data=data, follow_redirects=True)
    self.assertTrue(str(ticket.price * 5) in response.data, msg=response.data)
    soup = BeautifulSoup(response.data, 'html.parser')
    identifier = soup.select_one('input[name="identifier"]').get('value')
    return event, ticket, identifier

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

    def test_add_order_view(self):
        with app.test_request_context():
            event, ticket = get_event_ticket()
            response = self.app.get(url_for('event_ticket_sales.add_order', event_id=event.id), follow_redirects=True)
            self.assertTrue(str(ticket.name) in response.data, msg=response.data)

    def test_proceed_order_view(self):
        with app.test_request_context():
            order = create_order(self)

if __name__ == '__main__':
    unittest.main()

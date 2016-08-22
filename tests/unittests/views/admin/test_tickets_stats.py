import unittest
from datetime import datetime

from bs4 import BeautifulSoup
from flask import url_for

from app.helpers.data import save_to_db
from app.helpers.ticketing import TicketingManager
from app import current_app as app
from app.models.ticket_holder import TicketHolder
from tests.unittests.object_mother import ObjectMother
from tests.unittests.views.guest.test_ticketing import get_event_ticket
from tests.unittests.views.view_test_case import OpenEventViewTestCase

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

def create_discount_code(self):
    event = ObjectMother.get_event()
    save_to_db(event)
    data = {
        "code": "ABC_123",
        "value": "100",
        "value_type": "amount",
        "min_quantity": "1",
        "max_quantity": "2",
        "tickets_number": "30",
        "tickets[]": ["1", "2"]
    }
    response = self.app.post(url_for('event_ticket_sales.discount_codes_create', event_id=event.id),
                             data=data, follow_redirects=True)
    self.assertTrue(str(data['code']) in response.data, msg=response.data)
    return event, TicketingManager.get_discount_code(event.id, data['code'])

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
        holder = TicketHolder(firstname="John", lastname="Doe", order_id=order.id, ticket_id=ticket.id)
        save_to_db(holder)
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

    def test_discounts_list_view(self):
        with app.test_request_context():
            event, discount_code = create_discount_code(self)

    def test_check_duplicate_discount_code(self):
        with app.test_request_context():
            event, discount_code = create_discount_code(self)
            response = self.app.get(url_for('event_ticket_sales.check_duplicate_discount_code', event_id=event.id,
                                            code=discount_code.code),
                                    follow_redirects=True)
            self.assertEqual(response.status_code, 404)

            response = self.app.get(url_for('event_ticket_sales.check_duplicate_discount_code', event_id=event.id,
                                            code="BBB_123"),
                                    follow_redirects=True)
            self.assertEqual(response.status_code, 200)

            response = self.app.get(url_for('event_ticket_sales.check_duplicate_discount_code', event_id=event.id,
                                            code=discount_code.code, current=discount_code.id),
                                    follow_redirects=True)
            self.assertEqual(response.status_code, 200)

    def test_discounts_delete(self):
        with app.test_request_context():
            event, discount_code = create_discount_code(self)
            response = self.app.get(url_for('event_ticket_sales.discount_codes_delete', event_id=event.id,
                                    discount_code_id=discount_code.id), follow_redirects=True)
            self.assertFalse(TicketingManager.get_discount_code(event.id, discount_code.id), msg=response.data)

    def test_discounts_toggle(self):
        with app.test_request_context():
            event, discount_code = create_discount_code(self)
            response = self.app.get(url_for('event_ticket_sales.discount_codes_toggle', event_id=event.id,
                                    discount_code_id=discount_code.id), follow_redirects=True)
            self.assertFalse(TicketingManager.get_discount_code(event.id, discount_code.id).is_active,
                             msg=response.data)

    def test_discounts_edit(self):
        with app.test_request_context():
            event, discount_code = create_discount_code(self)
            response = self.app.get(url_for('event_ticket_sales.discount_codes_edit', event_id=event.id,
                                    discount_code_id=discount_code.id), follow_redirects=True)
            self.assertTrue(str(discount_code.code) in response.data, msg=response.data)
            data = {
                "code": "ABC_123",
                "value": "100",
                "value_type": "percent",
                "min_quantity": "1",
                "max_quantity": "2",
                "tickets_number": "30",
                "tickets[]": ["1", "2"]
            }
            response = self.app.post(url_for('event_ticket_sales.discount_codes_edit', event_id=event.id,
                                     discount_code_id=discount_code.id), data=data, follow_redirects=True)
            self.assertTrue(TicketingManager.get_discount_code(event.id, discount_code.id).type == 'percent',
                            msg=response.data)

if __name__ == '__main__':
    unittest.main()

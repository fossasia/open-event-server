import json
import unittest
from datetime import datetime, timedelta

from flask import url_for
from bs4 import BeautifulSoup

from app.helpers.data import save_to_db
from app.models.modules import Module
from app.models.ticket import Ticket
from tests.object_mother import ObjectMother
from tests.utils import OpenEventTestCase
from app import current_app as app
from app.helpers.ticketing import TicketingManager

def get_event_ticket():
    event = ObjectMother.get_event()
    event.name = 'Super Event'
    event.state = 'Published'
    save_to_db(event, "Event Saved")
    ticket = Ticket(name='Test Ticket',
                    type='paid',
                    sales_start=datetime.now() - timedelta(days=5),
                    sales_end=datetime.now() + timedelta(days=5),
                    description="SomeTicket",
                    event=event,
                    price=50)
    save_to_db(ticket, "Ticket Saved")
    save_to_db(Module(ticket_include=True, payment_include=True, donation_include=True))
    return event, ticket

def create_order(self):
    event, ticket = get_event_ticket()
    data = {
        "event_id": event.id,
        "ticket_ids[]": [ticket.id],
        "ticket_quantities[]": [5]
    }
    response = self.app.post(url_for('ticketing.create_order'), data=data, follow_redirects=True)
    self.assertTrue(str(ticket.price * 5) in response.data, msg=response.data)
    soup = BeautifulSoup(response.data, 'html.parser')
    identifier = soup.select_one('input[name="identifier"]').get('value')
    return event, ticket, identifier

class TestTicketingPage(OpenEventTestCase):

    def test_ticket_display(self):
        with app.test_request_context():
            event, ticket = get_event_ticket()
            response = self.app.get(url_for('event_detail.display_event_detail_home', event_id=event.id),
                                    follow_redirects=True)
            self.assertTrue("Test Ticket" in response.data, msg=response.data)

    def test_order_create(self):
        with app.test_request_context():
            create_order(self)

    def test_order_expire(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier), follow_redirects=True)
            self.assertEqual(response.status_code, 200, msg=response.status_code)
            order = TicketingManager.get_order_by_identifier(identifier)
            order.created_at = datetime.now() - timedelta(minutes=11)
            save_to_db(order)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier), follow_redirects=True)
            self.assertEqual(response.status_code, 404, msg=response.status_code)

    def test_order_payment(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            data = {
                "identifier": identifier,
                "email": "hola@tut.org",
                "firstname": "John",
                "lastname": "Doe",
                "address": "ACME Lane",
                "city": "Loony",
                "state": "Tunes",
                "zipcode": "1451145",
                "country": "Warner"
            }
            response = self.app.post(url_for('ticketing.initiate_order_payment'), data=data, follow_redirects=True)
            response_json = json.loads(response.data)
            self.assertEqual(data['email'], response_json['email'])
            order = TicketingManager.get_order_by_identifier(identifier)
            self.assertEqual(order.status, 'initialized')
            order.brand = "Visa"
            order.completed_at = datetime.now()
            order.status = "completed"
            order.last4 = "1234"
            order.exp_month = "12"
            order.exp_year = "2050"
            order.paid_via = "stripe"
            order.payment_mode = "card"
            save_to_db(order)
            response = self.app.get(url_for('ticketing.view_order_after_payment', order_identifier=identifier),
                                    follow_redirects=True)
            self.assertTrue("John" in response.data, msg=response.data)
            self.assertTrue("ACME Lane" in response.data, msg=response.data)
            self.assertTrue("1234" in response.data, msg=response.data)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 302, msg=response.status_code)
            response = self.app.get(url_for('ticketing.view_order_after_payment_pdf', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 200, msg=response.status_code)

if __name__ == '__main__':
    unittest.main()

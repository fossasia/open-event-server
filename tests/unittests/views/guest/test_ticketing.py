import json
import unittest
from datetime import datetime, timedelta
from os import environ

from flask import url_for
from bs4 import BeautifulSoup

from app.helpers.data import save_to_db
from app.models.modules import Module
from app.models.stripe_authorization import StripeAuthorization
from app.models.ticket import Ticket
from app.settings import set_settings
from tests.unittests.object_mother import ObjectMother
from tests.unittests.utils import OpenEventTestCase
from app import current_app as app
from app.helpers.ticketing import TicketingManager


def get_event_ticket():
    set_settings(paypal_mode='sandbox',
                 paypal_sandbox_username=environ.get('PAYPAL_SANDBOX_USERNAME', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 paypal_sandbox_password=environ.get('PAYPAL_SANDBOX_PASSWORD', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 paypal_sandbox_signature=environ.get('PAYPAL_SANDBOX_SIGNATURE', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 secret='super secret key')
    event = ObjectMother.get_event()
    event.name = 'Super Event'
    event.state = 'Published'
    event.paypal_email = 'donate-facilitator@fossasia.org'
    save_to_db(event, "Event Saved")
    stripe_auth = StripeAuthorization(
        stripe_secret_key=environ.get('STRIPE_SECRET_KEY', 'sk_test_SQPTVKtS8YvItGQuvHFvwve4'),
        stripe_refresh_token=environ.get('STRIPE_REFRESH_TOKEN', 'sk_test_SQPTVKtS8YvItGQuvHFvwve4'),
        stripe_publishable_key=environ.get('STRIPE_PUBLISHABLE_KEY', 'pk_test_e2jsd4RNUlYesCUb2KJ9nkCm'),
        stripe_user_id=environ.get('STRIPE_USER_ID', '1445522255'),
        stripe_email=environ.get('STRIPE_EMAIL', 'example@example.org'),
        event_id=event.id
    )
    save_to_db(stripe_auth, "StripeAuthorization Saved")
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
            response = self.app.get(url_for('event_detail.display_event_detail_home', identifier=event.identifier),
                                    follow_redirects=True)
            self.assertTrue(str(ticket.name) in response.data, msg=response.data)

    def test_order_create(self):
        with app.test_request_context():
            create_order(self)

    def test_order_expire(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier), follow_redirects=True)
            self.assertEqual(response.status_code, 200, msg=response.status_code)
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            order = TicketingManager.get_order_by_identifier(identifier)
            order.created_at = datetime.utcnow() - timedelta(minutes=11)
            save_to_db(order)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier), follow_redirects=True)
            self.assertEqual(response.status_code, 404, msg=response.status_code)

    def test_order_payment_stripe(self):
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
                "country": "Warner",
                "pay_via_service": "stripe"
            }
            response = self.app.post(url_for('ticketing.initiate_order_payment'), data=data, follow_redirects=True)
            response_json = json.loads(response.data)
            self.assertEqual(data['email'], response_json['email'], msg=response.data)
            self.assertEqual("start_stripe", response_json['action'], msg=response.data)
            order = TicketingManager.get_order_by_identifier(identifier)
            self.assertEqual(order.status, 'initialized', msg=response.data)
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
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            self.assertTrue(str(ticket.name) in response.data, msg=response.data)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 302, msg=response.status_code)
            response = self.app.get(url_for('ticketing.view_order_after_payment_pdf', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 200, msg=response.status_code)

    def test_order_payment_paypal(self):
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
                "country": "Warner",
                "pay_via_service": "paypal"
            }
            response = self.app.post(url_for('ticketing.initiate_order_payment'), data=data, follow_redirects=True)
            response_json = json.loads(response.data)
            self.assertEqual(data['email'], response_json['email'], msg=response.data)
            self.assertEqual("start_paypal", response_json['action'], msg=response.data)
            self.assertTrue("redirect_url" in response_json, msg=response.data)
            order = TicketingManager.get_order_by_identifier(identifier)
            self.assertEqual(order.status, 'initialized', msg=response.data)
            order.brand = "Visa"
            order.completed_at = datetime.now()
            order.status = "completed"
            order.paid_via = "paypal"
            order.transaction_id = "87906533255"
            save_to_db(order)
            response = self.app.get(url_for('ticketing.view_order_after_payment', order_identifier=identifier),
                                    follow_redirects=True)
            self.assertTrue("John" in response.data, msg=response.data)
            self.assertTrue("ACME Lane" in response.data, msg=response.data)
            self.assertTrue("87906533255" in response.data, msg=response.data)
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            self.assertTrue(str(ticket.name) in response.data, msg=response.data)
            response = self.app.get(url_for('ticketing.view_order', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 302, msg=response.status_code)
            response = self.app.get(url_for('ticketing.view_order_after_payment_pdf', order_identifier=identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 200, msg=response.status_code)

    def test_order_payment_paypal_cancel(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            response = self.app.get(
                url_for('ticketing.paypal_callback', order_identifier=identifier, function="cancel"),
                follow_redirects=True)
            order = TicketingManager.get_order_by_identifier(identifier)
            self.assertTrue(order.status == 'expired', msg=order.status)

    def test_order_payment_paypal_success(self):
        with app.test_request_context():
            event, ticket, identifier = create_order(self)
            response = self.app.get(
                url_for('ticketing.paypal_callback', order_identifier=identifier, function="success"),
                follow_redirects=True)
            self.assertTrue("error" in response.data, msg=response.data)


if __name__ == '__main__':
    unittest.main()

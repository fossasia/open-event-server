import json
import unittest
from datetime import datetime
from os import environ

from flask import url_for

from app.helpers.data import save_to_db
from app.models.event_invoice import EventInvoice
from app.settings import set_settings
from tests.object_mother import ObjectMother
from tests.utils import OpenEventTestCase
from app import current_app as app
from app.helpers.invoicing import InvoicingManager


def get_event_invoice():
    set_settings(paypal_mode='sandbox',
                 paypal_sandbox_username=environ.get('PAYPAL_SANDBOX_USERNAME', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 paypal_sandbox_password=environ.get('PAYPAL_SANDBOX_PASSWORD', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 paypal_sandbox_signature=environ.get('PAYPAL_SANDBOX_SIGNATURE', 'SQPTVKtS8YvItGQuvHFvwve4'),
                 stripe_secret_key='sk_test_SQPTVKtS8YvItGQuvHFvwve4',
                 stripe_publishable_key='pk_test_e2jsd4RNUlYesCUb2KJ9nkCm',
                 secret='super secret key')
    event = ObjectMother.get_event()
    event.name = 'Super Event'
    event.state = 'Published'
    user = ObjectMother.get_user()
    save_to_db(user)
    event.creator_id = user.id
    save_to_db(event, "Event Saved")
    new_invoice = EventInvoice(amount=100, event_id=event.id, user_id=event.creator_id)
    save_to_db(new_invoice, "Ticket Saved")
    return event, new_invoice


class TestInvoicing(OpenEventTestCase):

    def test_invoice_display(self):
        with app.test_request_context():
            event, invoice = get_event_invoice()

    def test_invoice_payment_stripe(self):
        with app.test_request_context():
            event, invoice = get_event_invoice()
            data = {
                "identifier": invoice.identifier,
                "email": "email@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "address": "ACME Lane",
                "city": "Loony",
                "state": "Tunes",
                "zipcode": "1451145",
                "country": "Warner",
                "pay_via_service": "stripe"
            }
            response = self.app.post(url_for('event_invoicing.initiate_invoice_payment'), data=data, follow_redirects=True)
            response_json = json.loads(response.data)
            self.assertEqual(data['email'], response_json['email'], msg=response.data)
            self.assertEqual("start_stripe", response_json['action'], msg=response.data)
            invoice = InvoicingManager.get_invoice_by_identifier(invoice.identifier)
            self.assertEqual(invoice.status, 'initialized', msg=response.data)
            invoice.brand = "Visa"
            invoice.completed_at = datetime.now()
            invoice.status = "completed"
            invoice.last4 = "1234"
            invoice.exp_month = "12"
            invoice.exp_year = "2050"
            invoice.paid_via = "stripe"
            invoice.payment_mode = "card"
            save_to_db(invoice)
            response = self.app.get(url_for('event_invoicing.view_invoice_after_payment', invoice_identifier=invoice.identifier),
                                    follow_redirects=True)
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            response = self.app.get(url_for('event_invoicing.view_invoice', invoice_identifier=invoice.identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 302, msg=response.status_code)
            response = self.app.get(url_for('event_invoicing.view_invoice_after_payment_pdf', invoice_identifier=invoice.identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 200, msg=response.status_code)

    def test_invoice_payment_paypal(self):
        with app.test_request_context():
            event, invoice = get_event_invoice()
            data = {
                "identifier": invoice.identifier,
                "email": "email@gmail.com",
                "firstname": "John",
                "lastname": "Doe",
                "address": "ACME Lane",
                "city": "Loony",
                "state": "Tunes",
                "zipcode": "1451145",
                "country": "Warner",
                "pay_via_service": "paypal"
            }
            response = self.app.post(url_for('event_invoicing.initiate_invoice_payment'), data=data, follow_redirects=True)
            response_json = json.loads(response.data)
            self.assertEqual(data['email'], response_json['email'], msg=response.data)
            self.assertEqual("start_paypal", response_json['action'], msg=response.data)
            self.assertTrue("redirect_url" in response_json, msg=response.data)
            invoice = InvoicingManager.get_invoice_by_identifier(invoice.identifier)
            self.assertEqual(invoice.status, 'initialized', msg=response.data)
            invoice.brand = "Visa"
            invoice.completed_at = datetime.now()
            invoice.status = "completed"
            invoice.paid_via = "paypal"
            invoice.transaction_id = "87906533255"
            save_to_db(invoice)
            response = self.app.get(url_for('event_invoicing.view_invoice_after_payment', invoice_identifier=invoice.identifier),
                                    follow_redirects=True)
            self.assertTrue(str(event.name) in response.data, msg=response.data)
            response = self.app.get(url_for('event_invoicing.view_invoice', invoice_identifier=invoice.identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 302, msg=response.status_code)
            response = self.app.get(url_for('event_invoicing.view_invoice_after_payment_pdf', invoice_identifier=invoice.identifier),
                                    follow_redirects=False)
            self.assertEqual(response.status_code, 200, msg=response.status_code)

    def test_invoice_payment_paypal_cancel(self):
        with app.test_request_context():
            event, invoice = get_event_invoice()
            response = self.app.get(
                url_for('event_invoicing.paypal_callback', invoice_identifier=invoice.identifier, function="cancel"),
                follow_redirects=True)
            invoice = InvoicingManager.get_invoice_by_identifier(invoice.identifier)
            self.assertTrue(invoice.status == 'cancelled', msg=invoice.status)

    def test_invoice_payment_paypal_success(self):
        with app.test_request_context():
            event, invoice = get_event_invoice()
            response = self.app.get(
                url_for('event_invoicing.paypal_callback', invoice_identifier=invoice.identifier, function="success"),
                follow_redirects=True)
            self.assertTrue("error" in response.data, msg=response.data)


if __name__ == '__main__':
    unittest.main()

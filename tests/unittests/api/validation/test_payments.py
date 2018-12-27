import unittest

import stripe
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.payment import StripePaymentsManager, PayPalPaymentsManager

from app.models.stripe_authorization import StripeAuthorization


class OrderInvoice:
    def __init__(self):
        self.user = {'email': 'test@gmail.com'}
        self.event = {'name': 'test_name'}
        self.user_id = '99999'
        self.event_id = '99999'
        self.amount = 75
        self.stripe_token = 'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'


class TestPaymentsTestCase(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        order_invoice = OrderInvoice()
        stripe_payments = StripePaymentsManager()

    def test_stripe_credentials(self):
        """
        Test stripe credentials without integer as parameter
        :return:
        """
        credentials = {}
        credentials['stripe_secret_key'] = 'sk_test_zgizVSrtc7DyWDMFPCACErVa'
        credentials["stripe_publishable_key"] = 'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'
        data = {
            'SECRET_KEY': credentials['stripe_secret_key'],
            'PUBLISHABLE_KEY': credentials["stripe_publishable_key"]
            }
        return self.assertEqual(stripe_payments.get_credentials(), data)

    def test_stripe_credentials_event_integer(self):
        """
        Test stripe credentials with integer as parameter
        :return:
        """
        event = 1
        authorization = StripeAuthorization.query.filter_by(event_id=event).first()
        data = {
                    'SECRET_KEY': authorization.stripe_secret_key,
                    'PUBLISHABLE_KEY': authorization.stripe_publishable_key
            }
        return self.assertEqual(stripe_payments.get_credentials(1), data)

    def test_capture_payment(self):
        """
        Testing payment capture
        :return:
        """
        credentials = {
            'secret_key': 'sk_test_zgizVSrtc7DyWDMFPCACErVa',
            'publishable_key': 'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'
        }
        currency = 'USD'
        stripe.api_key = credentials['publishable_key']
        captured_payment = stripe_payments.capture_payment(order_invoice, currency, credentials)
        charge_object_test = stripe.Charge()
        assert isinstance(captured_payment) == isinstance(charge_object_test)

    def tearDown(self):
        Setup.drop_db()

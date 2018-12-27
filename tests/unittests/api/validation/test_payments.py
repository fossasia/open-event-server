import unittest

from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.payment import StripePaymentsManager, PayPalPaymentsManager

from app.models.stripe_authorization import StripeAuthorization


class OrderInvoice:
    def __init__(self,user,amount,stripe_token):
      self.user = {'email':'test@gmail.com'}
      self.event = {'name':'test_name'}
      self.user_id = '99999'
      self.event_id = '99999'
      self.amount = 75
      self.stripe_token = 'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'


    
class TestPaymentsTestCase(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        order_invoice = OrderInvoice()
        
    
    def test_stripe_credentials(self):
        settings['stripe_secret_key'] = 'sk_test_zgizVSrtc7DyWDMFPCACErVa'
        settings["stripe_publishable_key"]= 'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'
        data = {
            'SECRET_KEY': settings['stripe_secret_key'],
            'PUBLISHABLE_KEY': settings["stripe_publishable_key"]
            }
        return self.assertEqual(get_credentials(),data)

    def test_stripe_credentials_event_integer(self):
        event = 1
        authorization = StripeAuthorization.query.filter_by(event_id=event).first()
        data = {
                    'SECRET_KEY': authorization.stripe_secret_key,
                    'PUBLISHABLE_KEY': authorization.stripe_publishable_key
            }
        return self.assertEqual(get_credentials(),data) 

    def test_charge(self):
        credentials = {
        'secret_key': 'sk_test_zgizVSrtc7DyWDMFPCACErVa',
        'publishable_key':'pk_test_GzzeUfMBivRmjuVICl5rpAJZ'
        }
        currency = 'USD'
        stripe.api_key = credentials['publishable_key']
        captured_payment = capture_payment()
        charge_object_test = stripe.Charge()
        assert type(captured_payment)==type(charge_object_test)

    
    def tearDown(self):
        Setup.drop_db()

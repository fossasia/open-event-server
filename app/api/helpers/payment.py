import json

import braintree
import requests
import stripe
from forex_python.converter import CurrencyRates

from app.api.helpers.cache import cache
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.utilities import represents_int
from app.models.stripe_authorization import StripeAuthorization
from app.settings import get_settings, Environment


@cache.memoize(5)
def forex(from_currency, to_currency, amount):
    try:
        currency_rates = CurrencyRates()
        return currency_rates.convert(from_currency, to_currency, amount)
    except:
        return amount


class StripePaymentsManager(object):
    @staticmethod
    def get_credentials(event=None):
        """
        If the event parameter is None, It returns the secret and publishable key of the Admin's Stripe account.
        Else, it returns the corresponding values for the event organizer's account.
        :param event:
        :return: Stripe secret and publishable keys.
        """
        if not event:
            settings = get_settings()
            if settings['stripe_secret_key'] and settings["stripe_publishable_key"] and settings[
                'stripe_secret_key'] != "" and \
                    settings["stripe_publishable_key"] != "":
                return {
                    'SECRET_KEY': settings['stripe_secret_key'],
                    'PUBLISHABLE_KEY': settings["stripe_publishable_key"]
                }
            else:
                return None
        else:
            if represents_int(event):
                authorization = StripeAuthorization.query.filter_by(event_id=event).first()
            else:
                authorization = event.stripe_authorization
            if authorization:
                return {
                    'SECRET_KEY': authorization.stripe_secret_key,
                    'PUBLISHABLE_KEY': authorization.stripe_publishable_key
                }
            else:
                return None

    @staticmethod
    def get_event_organizer_credentials_from_stripe(stripe_auth_code):
        """
        Uses the stripe_auth_code to get the other credentials for the event organizer's stripe account
        :param stripe_auth_code: stripe authorization code
        :return: response from stripe
        """
        credentials = StripePaymentsManager.get_credentials()

        if not credentials:
            raise ForbiddenException({'pointer': ''}, "Stripe payment isn't configured properly for this Event")

        data = {
            'client_secret': credentials['SECRET_KEY'],
            'code': stripe_auth_code,
            'grant_type': 'authorization_code'
        }

        response = requests.post('https://connect.stripe.com/oauth/token', data=data)
        return json.loads(response.text)

    @staticmethod
    def capture_payment(order_invoice, currency=None, credentials=None):
        if not credentials:
            credentials = StripePaymentsManager.get_credentials(order_invoice.event)

        if not credentials:
            raise Exception('Stripe is incorrectly configured')
        stripe.api_key = credentials['SECRET_KEY']

        if not currency:
            currency = order_invoice.event.payment_currency

        if not currency or currency == "":
            currency = "USD"

        try:
            customer = stripe.Customer.create(
                email=order_invoice.user.email,
                source=order_invoice.stripe_token
            )

            charge = stripe.Charge.create(
                customer=customer.id,
                amount=int(order_invoice.amount * 100),
                currency=currency.lower(),
                metadata={
                    'order_id': order_invoice.id,
                    'event': order_invoice.event.name,
                    'user_id': order_invoice.user_id,
                    'event_id': order_invoice.event_id
                },
                description=order_invoice.event.name
            )
            return charge
        except:
            return None


class PayPalPaymentsManager(object):
    """
    Class to manage payment through Paypal Braintree.
    """

    @staticmethod
    def get_credentials():
        """
        Initialize and return the Braintree payment gateway.
        :return: Braintree gateway instance.
        """
        # Use Sandbox by default.
        settings = get_settings()
        paypal_braintree_access_token = settings['paypal_braintree_sandbox_access_token']

        # Switch to production if environment is production.
        if settings['paypal_mode'] == Environment.PRODUCTION:
            paypal_braintree_access_token = settings['paypal_braintree_access_token']

        # Initialize braintree instance.
        braintree_payment_gateway_instance = braintree.BraintreeGateway(access_token=paypal_braintree_access_token)

        return braintree_payment_gateway_instance

    @staticmethod
    def get_client_token():
        """
        Get the client token for Braintree client SDK.
        :return: token.
        """
        braintree_payment_gateway = PayPalPaymentsManager.get_credentials()
        return braintree_payment_gateway.client_token.generate()

    @staticmethod
    def create_transaction(order_invoice, paypal_braintree_nonce):
        """
        Create transaction and charge the user.
        :param order_invoice: Order to charge for.
        :param paypal_braintree_nonce: Nonce received from Paypal Braintree.
        :return: Result of the transaction.
        """
        braintree_payment_gateway = PayPalPaymentsManager.get_credentials()

        # submit_for_settlement ensures that the funds are captured instantly.
        result = braintree_payment_gateway.transaction.sale({
            "amount": int(order_invoice.amount * 100),
            "merchant_account_id": order_invoice.event.payment_currency,
            "payment_method_nonce": paypal_braintree_nonce,
            "options": {
                "submit_for_settlement": True
            }
        })

        return result

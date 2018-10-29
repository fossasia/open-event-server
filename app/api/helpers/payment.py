import json

import paypalrestsdk
import requests
import stripe
from forex_python.converter import CurrencyRates

from app.api.helpers.cache import cache
from app.api.helpers.exceptions import ForbiddenException, ConflictException
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
    """
    Class to manage payments through Stripe.
    """

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
            raise ForbiddenException({'pointer': ''}, "Stripe payment isn't configured properly for the Platform")

        data = {
            'client_secret': credentials['SECRET_KEY'],
            'code': stripe_auth_code,
            'grant_type': 'authorization_code'
        }

        response = requests.post('https://connect.stripe.com/oauth/token', data=data)
        return json.loads(response.text)

    @staticmethod
    def capture_payment(order_invoice, currency=None, credentials=None):
        """
        Capture payments through stripe.
        :param order_invoice: Order to be charged for
        :param currency: Currency of the order amount.
        :param credentials: Stripe credentials.
        :return: charge/None depending on success/failure.
        """
        if not credentials:
            credentials = StripePaymentsManager.get_credentials(order_invoice.event)

        if not credentials:
            raise ConflictException({'pointer': ''},
                                    'Stripe credentials not found for the event.')
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
        except Exception as e:
            raise ConflictException({'pointer': ''}, str(e))


class PayPalPaymentsManager(object):
    """
    Class to manage payment through Paypal REST API.
    """

    @staticmethod
    def configure_paypal():
        """
        Configure the paypal sdk
        :return: Credentials
        """
        # Use Sandbox by default.
        settings = get_settings()
        paypal_mode = 'sandbox'
        paypal_client = settings.get('paypal_sandbox_client', None)
        paypal_secret = settings.get('paypal_sandbox_secret', None)

        # Switch to production if paypal_mode is production.
        if settings['paypal_mode'] == Environment.PRODUCTION:
            paypal_mode = 'live'
            paypal_client = settings.get('paypal_client', None)
            paypal_secret = settings.get('paypal_secret', None)

        if not paypal_client or not paypal_secret:
            raise ConflictException({'pointer': ''}, "Payments through Paypal hasn't been configured on the platform")

        paypalrestsdk.configure({
            "mode": paypal_mode,
            "client_id": paypal_client,
            "client_secret": paypal_secret})

    @staticmethod
    def create_payment(order, return_url, cancel_url):
        """
        Create payment for an order
        :param order: Order to create payment for.
        :param return_url: return url for the payment.
        :param cancel_url: cancel_url for the payment.
        :return: request_id or the error message along with an indicator.
        """
        if (not order.event.paypal_email) or order.event.paypal_email == '':
            raise ConflictException({'pointer': ''}, "Payments through Paypal hasn't been configured for the event")

        PayPalPaymentsManager.configure_paypal()

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {"payment_method": "paypal"},
            "redirect_urls": {
                "return_url": return_url,
                "cancel_url": cancel_url},
            "transactions": [{
                "amount": {
                    "total": int(order.amount),
                    "currency": order.event.payment_currency
                },
                "payee": {
                    "email": order.event.paypal_email
                }
            }]
        })

        if payment.create():
            return True, payment.id
        else:
            return False, payment.error

    @staticmethod
    def execute_payment(paypal_payer_id, paypal_payment_id):
        """
        Execute payemnt and charge the user.
        :param paypal_payment_id: payment_id
        :param paypal_payer_id: payer_id
        :return: Result of the transaction.
        """

        payment = paypalrestsdk.Payment.find(paypal_payment_id)

        if payment.execute({"payer_id": paypal_payer_id}):
            return True, 'Successfully Executed'
        else:
            return False, payment.error

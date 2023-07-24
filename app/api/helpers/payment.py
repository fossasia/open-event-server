import json

import omise
import paypalrestsdk
import requests
import stripe
from forex_python.converter import CurrencyRates

from app.api.helpers import checksum
from app.api.helpers.cache import cache
from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.errors import ConflictError, ForbiddenError
from app.api.helpers.utilities import represents_int, round_money
from app.models.order import Order
from app.models.stripe_authorization import StripeAuthorization
from app.settings import Environment, get_settings


@cache.memoize(5)
def forex(from_currency, to_currency, amount):
    try:
        currency_rates = CurrencyRates()
        return currency_rates.convert(from_currency, to_currency, amount)
    except:
        return amount


class StripePaymentsManager:
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
            # Perform refresh from db to make sure Stripe keys are retrieved
            settings = get_settings(from_db=True)
            if (
                settings['app_environment'] == 'development'
                and settings['stripe_test_secret_key']
                and settings['stripe_test_publishable_key']
            ):
                return {
                    'SECRET_KEY': settings['stripe_test_secret_key'],
                    'PUBLISHABLE_KEY': settings["stripe_test_publishable_key"],
                }
            if settings['stripe_secret_key'] and settings["stripe_publishable_key"]:
                return {
                    'SECRET_KEY': settings['stripe_secret_key'],
                    'PUBLISHABLE_KEY': settings["stripe_publishable_key"],
                }
            return None
        if represents_int(event):
            authorization = StripeAuthorization.query.filter_by(event_id=event).first()
        else:
            authorization = event.stripe_authorization
        if authorization:
            return {
                'SECRET_KEY': authorization.stripe_secret_key,
                'PUBLISHABLE_KEY': authorization.stripe_publishable_key,
            }
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
            raise ForbiddenError(
                {'pointer': ''},
                "Stripe payment isn't configured properly for the Platform",
            )

        data = {
            'client_secret': credentials['SECRET_KEY'],
            'code': stripe_auth_code,
            'grant_type': 'authorization_code',
        }

        response = requests.post('https://connect.stripe.com/oauth/token', data=data)
        return json.loads(response.text)

    @staticmethod
    def get_payment_intent_stripe(order_invoice, currency=None, credentials=None):
        """
        Capture payments through stripe.
        :param order_invoice: Order to be charged for
        :param currency: Currency of the order amount.
        :param credentials: Stripe credentials.
        :return: secret of payment intent
        """
        if not credentials:
            credentials = StripePaymentsManager.get_credentials(order_invoice.event)

        if not credentials:
            raise ConflictError(
                {'pointer': ''}, 'Stripe credentials not found for the event.'
            )
        stripe.api_key = credentials['SECRET_KEY']
        if not currency:
            currency = order_invoice.event.payment_currency

        if not currency or currency == "":
            currency = "USD"

        event_name = order_invoice.event.name

        try:
            payment_intent = stripe.PaymentIntent.create(
                amount=int(order_invoice.amount * 100),
                currency=currency.lower(),
                metadata={'order_id': order_invoice.identifier},
                automatic_payment_methods={
                    'enabled': True,
                },
                description=f"Eventyay {event_name}"
            )
            return payment_intent

        except Exception as e:
            raise ConflictError({'pointer': ''}, str(e))

    @staticmethod
    def retrieve_session(event_id, stripe_session_id):
        credentials = StripePaymentsManager.get_credentials(event_id)

        if not credentials:
            raise ConflictError(
                {'pointer': ''}, 'Stripe credentials not found for the event.'
            )
        stripe.api_key = credentials['SECRET_KEY']
        session = stripe.checkout.Session.retrieve(stripe_session_id)

        return session

    @staticmethod
    def retrieve_payment_intent(event_id, payment_intent_id):
        credentials = StripePaymentsManager.get_credentials(event_id)

        if not credentials:
            raise ConflictError(
                {'pointer': ''}, 'Stripe credentials not found for the event.'
            )
        stripe.api_key = credentials['SECRET_KEY']
        payment_intent = stripe.PaymentIntent.retrieve(payment_intent_id)

        return payment_intent


class PayPalPaymentsManager:
    """
    Class to manage payment through Paypal REST API.
    """

    @staticmethod
    def configure_paypal():
        """
        Configure the paypal sdk
        :return: Credentials
        """
        settings = get_settings()
        # Use Sandbox by default.
        paypal_mode = settings.get(
            'paypal_mode',
            'live'
            if (settings['app_environment'] == Environment.PRODUCTION)
            else 'sandbox',
        )
        paypal_key = None
        if paypal_mode == 'sandbox':
            paypal_key = 'paypal_sandbox'
        elif paypal_mode == 'live':
            paypal_key = 'paypal'

        if not paypal_key:
            raise ConflictError(
                {'pointer': ''}, "Paypal Mode must be 'live' or 'sandbox'"
            )

        paypal_client = settings.get(f'{paypal_key}_client', None)
        paypal_secret = settings.get(f'{paypal_key}_secret', None)

        if not paypal_client or not paypal_secret:
            raise ConflictError(
                {'pointer': ''},
                "Payments through Paypal have not been configured on the platform",
            )
        return paypalrestsdk.configure(
            {
                "mode": paypal_mode,
                "client_id": paypal_client,
                "client_secret": paypal_secret,
            }
        )

    @staticmethod
    def create_payment(order, return_url, cancel_url, payee_email=None):
        """
        Create payment for an order
        :param order: Order to create payment for.
        :param return_url: return url for the payment.
        :param cancel_url: cancel_url for the payment.
        :param payee_email: email of the payee. Default to event paypal email if not set
        :return: request_id or the error message along with an indicator.
        """
        payee_email = payee_email or order.event.paypal_email
        if not payee_email:
            raise ConflictError(
                {'pointer': ''},
                "Payments through Paypal hasn't been configured for the billing",
            )

        PayPalPaymentsManager.configure_paypal()

        payment = paypalrestsdk.Payment(
            {
                "intent": "sale",
                "payer": {"payment_method": "paypal"},
                "redirect_urls": {"return_url": return_url, "cancel_url": cancel_url},
                "transactions": [
                    {
                        "amount": {
                            "total": float(round_money(order.amount)),
                            "currency": order.event.payment_currency,
                        },
                        "payee": {"email": payee_email},
                    }
                ],
            }
        )

        if payment.create():
            return True, payment.id
        return False, payment.error

    @staticmethod
    def verify_payment(payment_id, order):
        """
        Verify Paypal payment one more time for paying with Paypal in mobile client
        """
        PayPalPaymentsManager.configure_paypal()
        try:
            payment_server = paypalrestsdk.Payment.find(payment_id)
            if payment_server.state != 'approved':
                return (
                    False,
                    'Payment has not been approved yet. Status is '
                    + payment_server.state
                    + '.',
                )

            # Get the most recent transaction
            transaction = payment_server.transactions[0]
            amount_server = transaction.amount.total
            currency_server = transaction.amount.currency
            sale_state = transaction.related_resources[0].sale.state

            if float(amount_server) != order.amount:
                return False, 'Payment amount does not match order'
            if currency_server != order.event.payment_currency:
                return False, 'Payment currency does not match order'
            if sale_state != 'completed':
                return False, 'Sale not completed'
            if PayPalPaymentsManager.used_payment(payment_id, order):
                return False, 'Payment already been verified'
            return True, None
        except paypalrestsdk.ResourceNotFound:
            return False, 'Payment Not Found'

    @staticmethod
    def used_payment(payment_id, order):
        """
        Function to check for recycling of payment IDs
        """
        if Order.query.filter(Order.paypal_token == payment_id).first() is None:
            order.paypal_token = payment_id
            save_to_db(order)
            return False
        return True

    @staticmethod
    def execute_payment(paypal_payer_id, paypal_payment_id):
        """
        Execute payemnt and charge the user.
        :param paypal_payment_id: payment_id
        :param paypal_payer_id: payer_id
        :return: Result of the transaction.
        """
        PayPalPaymentsManager.configure_paypal()
        payment = paypalrestsdk.Payment.find(paypal_payment_id)

        if payment.execute({"payer_id": paypal_payer_id}):
            return True, 'Successfully Executed'
        return False, payment.error


class AliPayPaymentsManager:
    """
    Class to manage AliPay Payments
    """

    @staticmethod
    def create_source(amount, currency, redirect_return_uri):
        stripe.api_key = get_settings()['alipay_publishable_key']
        response = stripe.Source.create(
            type='alipay',
            currency=currency,
            amount=amount,
            redirect={'return_url': redirect_return_uri},
        )
        return response

    @staticmethod
    def charge_source(order_identifier):
        order = safe_query(Order, 'identifier', order_identifier, 'identifier')
        stripe.api_key = get_settings()['alipay_secret_key']
        charge = stripe.Charge.create(
            amount=int(order.amount),
            currency=order.event.payment_currency,
            source=order.order_notes,
        )
        return charge


class OmisePaymentsManager:
    """
    Class to manage Omise Payments
    """

    @staticmethod
    def charge_payment(order_identifier, token):
        if get_settings()['app_environment'] == Environment.PRODUCTION:
            omise.api_secret = get_settings()['omise_test_secret']
            omise.api_public = get_settings()['omise_test_public']
        else:
            omise.api_secret = get_settings()['omise_test_secret']
            omise.api_public = get_settings()['omise_test_public']
        order = safe_query(Order, 'identifier', order_identifier, 'identifier')
        charge = omise.Charge.create(
            amount=int(round(order.amount)),
            currency=order.event.payment_currency,
            card=token,
            metadata={"order_id": str(order_identifier), "status": True},
        )
        return charge


class PaytmPaymentsManager:
    """
    Class to manage PayTM payments
    """

    @property
    def paytm_endpoint(self):
        if get_settings()['paytm_mode'] == 'test':
            url = "https://securegw-stage.paytm.in/theia/api/v1/"
        else:
            url = "https://securegw.paytm.in/theia/api/v1/"
        return url

    @staticmethod
    def generate_checksum(paytm_params):
        if get_settings()['paytm_mode'] == 'test':
            merchant_key = get_settings()['paytm_sandbox_secret']
        else:
            merchant_key = get_settings()['paytm_live_secret']
        return checksum.generate_checksum_by_str(
            json.dumps(paytm_params["body"]), merchant_key
        )

    @staticmethod
    def hit_paytm_endpoint(url, head, body=None):
        paytm_params = {}
        paytm_params["body"] = body
        paytm_params["head"] = head
        post_data = json.dumps(paytm_params)
        response = requests.post(
            url, data=post_data, headers={"Content-type": "application/json"}
        ).json()
        return response

import requests
import sqlalchemy
import stripe
import urllib.parse
from flask import current_app
from forex_python.converter import CurrencyRates
from urllib.parse import urlencode

from app.api.helpers.cache import cache
from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.files import make_frontend_url
from app.api.helpers.utilities import represents_int
from app.models import db
from app.models.event import Event
from app.models.order import Order
from app.models.stripe_authorization import StripeAuthorization
from app.models.ticket_fee import TicketFees
from app.settings import get_settings

DEFAULT_FEE = 0.0


@cache.memoize(5)
def forex(from_currency, to_currency, amount):
    try:
        currency_rates = CurrencyRates()
        return currency_rates.convert(from_currency, to_currency, amount)
    except:
        return amount


@cache.memoize(5)
def get_fee(currency):
    fee = TicketFees.query.filter_by(currency=currency).order_by(sqlalchemy.desc(TicketFees.id)).first()
    if fee:
        return fee.service_fee
    else:
        return DEFAULT_FEE


class StripePaymentsManager(object):

    @staticmethod
    def get_credentials(event=None):
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
                authorization = event.stripe
            if authorization:
                return {
                    'SECRET_KEY': authorization.stripe_secret_key,
                    'PUBLISHABLE_KEY': authorization.stripe_publishable_key
                }
            else:
                return None

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
    api_version = 93

    @staticmethod
    def get_credentials(event=None, override_mode=False, is_testing=False):
        if event and represents_int(event):
            event = safe_query(db, Event, 'id', event, 'event_id')
        settings = get_settings()
        if not override_mode:
            if settings['paypal_mode'] and settings['paypal_mode'] != "":
                if settings['paypal_mode'] == 'live':
                    is_testing = False
                else:
                    is_testing = True
            else:
                return None

        if is_testing:
            credentials = {
                'USER': settings['paypal_sandbox_username'],
                'PWD': settings['paypal_sandbox_password'],
                'SIGNATURE': settings['paypal_sandbox_signature'],
                'SERVER': 'https://api-3t.sandbox.paypal.com/nvp',
                'CHECKOUT_URL': 'https://www.sandbox.paypal.com/cgi-bin/webscr',
                'EMAIL': '' if not event or not event.paypal_email or event.paypal_email == "" else event.paypal_email
            }
        else:
            credentials = {
                'USER': settings['paypal_live_username'],
                'PWD': settings['paypal_live_password'],
                'SIGNATURE': settings['paypal_live_signature'],
                'SERVER': 'https://api-3t.paypal.com/nvp',
                'CHECKOUT_URL': 'https://www.paypal.com/cgi-bin/webscr',
                'EMAIL': '' if not event or not event.paypal_email or event.paypal_email == "" else event.paypal_email
            }
        if credentials['USER'] and credentials['PWD'] and credentials['SIGNATURE'] and credentials['USER'] != "" and \
                credentials['PWD'] != "" and credentials['SIGNATURE'] != "":
            return credentials
        else:
            return None

    @staticmethod
    def get_checkout_url(order, currency=None, credentials=None):
        if not credentials:
            credentials = PayPalPaymentsManager.get_credentials(order.event)

        if not credentials:
            raise Exception('PayPal credentials have not be set correctly')

        if current_app.config['TESTING']:
            return credentials['CHECKOUT_URL']

        currency = order.event.payment_currency if not currency and order.event.payment_currency != "" else "USD"
        data = {
            'USER': credentials['USER'],
            'PWD': credentials['PWD'],
            'SIGNATURE': credentials['SIGNATURE'],
            'SUBJECT': credentials['EMAIL'],

            'METHOD': 'SetExpressCheckout',
            'VERSION': PayPalPaymentsManager.api_version,
            'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE',
            'PAYMENTREQUEST_0_AMT': order.amount,
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
            'RETURNURL': make_frontend_url(path='/orders/{identifier}/payment/success'.
                                           format(identifier=order.identifier)),
            'CANCELURL': make_frontend_url(path='/orders/{identifier}/payment/cancelled'.
                                           format(identifier=order.identifier))
        }

        count = 1

        if type(order) is Order:
            for ticket_order in order.order_tickets:
                data['L_PAYMENTREQUEST_' + str(count) + '_NAMEm'] = ticket_order.ticket.name
                data['L_PAYMENTREQUEST_' + str(count) + '_QTYm'] = ticket_order.quantity
                data['L_PAYMENTREQUEST_' + str(count) + '_AMTm'] = ticket_order.ticket.price
                count += 1

        response = requests.post(credentials['SERVER'], data=data)
        if 'TOKEN' not in dict(urllib.parse.parse_qsl(response.text)):
            raise Exception('PayPal Token could not be retrieved')
        token = dict(urllib.parse.parse_qsl(response.text))['TOKEN']
        order.paypal_token = token
        save_to_db(order)
        return credentials['CHECKOUT_URL'] + "?" + urlencode({
            'cmd': '_express-checkout',
            'token': token
        })

    @staticmethod
    def get_approved_payment_details(order, credentials=None):

        if not credentials:
            credentials = PayPalPaymentsManager.get_credentials(order.event)

        if not credentials:
            raise Exception('PayPal credentials have not be set correctly')

        data = {
            'USER': credentials['USER'],
            'PWD': credentials['PWD'],
            'SIGNATURE': credentials['SIGNATURE'],
            'SUBJECT': credentials['EMAIL'],
            'METHOD': 'GetExpressCheckoutDetails',
            'VERSION': PayPalPaymentsManager.api_version,
            'TOKEN': order.paypal_token
        }

        if current_app.config['TESTING']:
            return data

        response = requests.post(credentials['SERVER'], data=data)
        return dict(urllib.parse.parse_qsl(response.text))

    @staticmethod
    def capture_payment(order, payer_id, currency=None, credentials=None):
        if not credentials:
            credentials = PayPalPaymentsManager.get_credentials(order.event)

        if not credentials:
            raise Exception('PayPal credentials have not be set correctly')

        if not currency:
            currency = order.event.payment_currency

        if not currency or currency == "":
            currency = "USD"

        data = {
            'USER': credentials['USER'],
            'PWD': credentials['PWD'],
            'SIGNATURE': credentials['SIGNATURE'],
            'SUBJECT': credentials['EMAIL'],
            'METHOD': 'DoExpressCheckoutPayment',
            'VERSION': PayPalPaymentsManager.api_version,
            'TOKEN': order.paypal_token,
            'PAYERID': payer_id,
            'PAYMENTREQUEST_0_PAYMENTACTION': 'SALE',
            'PAYMENTREQUEST_0_AMT': order.amount,
            'PAYMENTREQUEST_0_CURRENCYCODE': currency,
        }

        response = requests.post(credentials['SERVER'], data=data)
        return dict(urllib.parse.parse_qsl(response.text))

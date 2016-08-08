"""Copyright 2016 Niranjan Rajendran"""
import urlparse
from urllib import urlencode

import stripe
from flask import url_for, current_app

import requests

from app.helpers.data_getter import DataGetter
from app.helpers.data import save_to_db
from app.models.stripe_authorization import StripeAuthorization
from app.settings import get_settings

def represents_int(string):
    try:
        int(string)
        return True
    except:
        return False


class StripePaymentsManager(object):

    @staticmethod
    def get_credentials(event=None):
        if not event:
            settings = get_settings()
            if settings.stripe_secret_key and settings.stripe_publishable_key and settings.stripe_secret_key != "" and \
                    settings.stripe_publishable_key != "":
                return {
                    'SECRET_KEY': settings.stripe_secret_key,
                    'PUBLISHABLE_KEY': settings.stripe_publishable_key
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
    def capture_payment(order, currency=None):

        credentials = StripePaymentsManager.get_credentials(order.event)
        if not credentials:
            raise Exception('Stripe is incorrectly configured')

        stripe.api_key = credentials['SECRET_KEY']

        if not currency:
            currency = order.event.payment_currency

        if not currency or currency == "":
            currency = "USD"

        try:
            customer = stripe.Customer.create(
                email=order.user.email,
                source=order.stripe_token
            )

            charge = stripe.Charge.create(
                customer=customer.id,
                amount=int(order.amount * 100),
                currency=currency.lower(),
                metadata={
                    'order_id': order.id,
                    'event': order.event.name,
                    'user_id': order.user_id,
                    'event_id': order.event_id
                },
                description=order.event.name + " ticket(s)"
            )
            return charge
        except:
            return None

class PayPalPaymentsManager(object):

    api_version = 93

    @staticmethod
    def get_credentials(event, override_mode=False, is_testing=False):
        if represents_int(event):
            event = DataGetter.get_event(event)

        if not event:
            return None

        if not event.paypal_email or event.paypal_email == "":
            return None

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
                'EMAIL': event.paypal_email
            }
        else:
            credentials = {
                'USER': settings['paypal_live_username'],
                'PWD': settings['paypal_live_password'],
                'SIGNATURE': settings['paypal_live_signature'],
                'SERVER': 'https://api-3t.paypal.com/nvp',
                'CHECKOUT_URL': 'https://www.paypal.com/cgi-bin/webscr',
                'EMAIL': event.paypal_email
            }

        if credentials['USER'] and credentials['USER'] and credentials['USER'] and credentials['USER'] != "" and \
                credentials['USER'] != "" and credentials['USER'] != "":
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

        if not currency:
            currency = order.event.payment_currency

        if not currency or currency == "":
            currency = "USD"

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
            'RETURNURL': url_for('ticketing.paypal_callback', order_identifier=order.identifier,
                                 function='success', _external=True),
            'CANCELURL': url_for('ticketing.paypal_callback', order_identifier=order.identifier,
                                 function='cancel', _external=True)
        }

        count = 1
        for ticket_order in order.tickets:
            data['L_PAYMENTREQUEST_' + str(count) + '_NAMEm'] = ticket_order.ticket.name
            data['L_PAYMENTREQUEST_' + str(count) + '_QTYm'] = ticket_order.quantity
            data['L_PAYMENTREQUEST_' + str(count) + '_AMTm'] = ticket_order.ticket.price
            count += 1

        response = requests.post(credentials['SERVER'], data=data)
        token = dict(urlparse.parse_qsl(response.text))['TOKEN']
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
        return dict(urlparse.parse_qsl(response.text))

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
        return dict(urlparse.parse_qsl(response.text))

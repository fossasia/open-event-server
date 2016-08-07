"""Copyright 2016 Niranjan Rajendran"""
from app.helpers.ticketing import represents_int
from app.models.stripe_authorization import StripeAuthorization
from app.settings import get_settings


class PaymentsManager(object):

    @staticmethod
    def get_stripe_credentials(event=None):
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
    def get_paypal_credentials(override_mode=False, is_testing=False):
        settings = get_settings()

        if not override_mode:
            if settings.paypal_mode and settings.paypal_mode != "":
                if settings.paypal_mode == 'live':
                    is_testing = False
                else:
                    is_testing = True
            else:
                return None

        if is_testing:
            credentials = {
                'USER': settings.paypal_sandbox_username,
                'PWD': settings.paypal_sandbox_password,
                'SIGNATURE': settings.paypal_sandbox_signature
            }
        else:
            credentials = {
                'USER': settings.paypal_live_username,
                'PWD': settings.paypal_live_password,
                'SIGNATURE': settings.paypal_live_signature
            }

        if credentials['USER'] and credentials['USER'] and credentials['USER'] and credentials['USER'] != "" and \
                credentials['USER'] != "" and credentials['USER'] != "":
            return credentials
        else:
            return None


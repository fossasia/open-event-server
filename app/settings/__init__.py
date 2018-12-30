import stripe
from flask import current_app
from sqlalchemy import desc

from app.models.ticket_fee import TicketFees
from app.models.setting import Setting, Environment


def get_settings(from_db=False):
    """
    Use this to get latest system settings
    """
    if not from_db and 'custom_settings' in current_app.config:
        return current_app.config['custom_settings']
    s = Setting.query.order_by(desc(Setting.id)).first()
    if s is None:
        set_settings(secret='super secret key', app_name='Open Event')
    else:
        current_app.config['custom_settings'] = make_dict(s)
        if not current_app.config['custom_settings'].get('secret'):
            set_settings(secret='super secret key', app_name='Open Event')
    return current_app.config['custom_settings']


def refresh_settings():
    # Force fetch settings from DB, thus refreshing it
    get_settings(from_db=True)


def get_setts():
    return Setting.query.order_by(desc(Setting.id)).first()


def set_settings(**kwargs):
    """
    Update system settings
    """

    if 'service_fee' in kwargs:
        ticket_service_fees = kwargs.get('service_fee')
        ticket_maximum_fees = kwargs.get('maximum_fee')
        from app.api.helpers.data_getter import DataGetter
        from app.api.helpers.db import save_to_db
        currencies = DataGetter.get_payment_currencies()
        ticket_fees = DataGetter.get_fee_settings()
        if not ticket_fees:
            for i, (currency, has_paypal, has_stripe) in enumerate(currencies):
                currency = currency.split(' ')[0]
                if float(ticket_maximum_fees[i]) == 0.0:
                    ticket_maximum_fees[i] = ticket_service_fees[i]
                ticket_fee = TicketFees(currency=currency,
                                        service_fee=ticket_service_fees[i],
                                        maximum_fee=ticket_maximum_fees[i])
                save_to_db(ticket_fee, "Ticket Fees settings saved")
        else:
            i = 0
            for fee in ticket_fees:
                if float(ticket_maximum_fees[i]) == 0.0:
                    ticket_maximum_fees[i] = ticket_service_fees[i]
                fee.service_fee = ticket_service_fees[i]
                fee.maximum_fee = ticket_maximum_fees[i]
                save_to_db(fee, "Fee Options Updated")
                i += 1
    else:
        setting = Setting.query.order_by(desc(Setting.id)).first()
        if not setting:
            setting = Setting(**kwargs)
        else:
            for key, value in list(kwargs.items()):
                setattr(setting, key, value)
        from app.api.helpers.db import save_to_db
        save_to_db(setting, 'Setting saved')
        current_app.secret_key = setting.secret
        stripe.api_key = setting.stripe_secret_key

        if setting.app_environment == Environment.DEVELOPMENT and not current_app.config['DEVELOPMENT']:
            current_app.config.from_object('config.DevelopmentConfig')

        if setting.app_environment == Environment.STAGING and not current_app.config['STAGING']:
            current_app.config.from_object('config.StagingConfig')

        if setting.app_environment == Environment.PRODUCTION and not current_app.config['PRODUCTION']:
            current_app.config.from_object('config.ProductionConfig')

        if setting.app_environment == Environment.TESTING and not current_app.config['TESTING']:
            current_app.config.from_object('config.TestingConfig')

        current_app.config['custom_settings'] = make_dict(setting)


def make_dict(s):
    arguments = {}
    for name, column in list(s.__mapper__.columns.items()):
        if not (column.primary_key or column.unique):
            arguments[name] = getattr(s, name)
    return arguments

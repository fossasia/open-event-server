import stripe
from flask import current_app
from sqlalchemy import desc
from app.models.setting import Setting
from app.models.fees import TicketFees


def get_settings():
    """
    Use this to get latest system settings
    """
    if 'custom_settings' in current_app.config:
        return current_app.config['custom_settings']
    s = Setting.query.order_by(desc(Setting.id)).first()
    if s is None:
        set_settings(secret='super secret key')
    else:
        current_app.config['custom_settings'] = make_dict(s)
    return current_app.config['custom_settings']


def set_settings(**kwargs):
    """
    Update system settings
    """

    if 'service_fee' in kwargs:
        ticket_service_fees = kwargs.get('service_fee')
        ticket_maximum_fees = kwargs.get('maximum_fee')
        from app.helpers.data_getter import DataGetter
        from app.helpers.data import save_to_db
        currencies = DataGetter.get_payment_currencies()
        for i, (currency, has_paypal, has_stripe) in enumerate(currencies):
            currency = currency.split(' ')[0]
            ticket_fee = TicketFees(currency=currency,
                                    service_fee=ticket_service_fees[i],
                                    maximum_fee=ticket_maximum_fees[i])
            save_to_db(ticket_fee, "Ticket Fees settings saved")
    else:
        setting = Setting.query.first()
        if not setting:
            setting = Setting(**kwargs)
        else:
            for key, value in kwargs.iteritems():
                setattr(setting, key, value)
        from app.helpers.data import save_to_db
        save_to_db(setting, 'Setting saved')
        current_app.secret_key = setting.secret
        stripe.api_key = setting.stripe_secret_key
        current_app.config['custom_settings'] = make_dict(setting)


def make_dict(s):
    arguments = {}
    for name, column in s.__mapper__.columns.items():
        if not (column.primary_key or column.unique):
            arguments[name] = getattr(s, name)
    return arguments

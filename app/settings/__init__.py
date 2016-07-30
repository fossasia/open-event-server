import stripe
from flask import current_app
from sqlalchemy import desc
from app.models.setting import Setting


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
    setting = Setting(**kwargs)
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

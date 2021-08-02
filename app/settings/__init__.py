import stripe
from flask import current_app
from sqlalchemy import desc

from app.models.setting import Environment, Setting


def get_settings(from_db=False):
    """
    Use this to get latest system settings
    """
    if not from_db and 'custom_settings' in current_app.config:
        return current_app.config['custom_settings']
    s = Setting.query.order_by(desc(Setting.id)).first()
    app_environment = current_app.config.get('ENV', 'production')
    if s is None:
        set_settings(app_name='Open Event', app_environment=app_environment)
    else:
        current_app.config['custom_settings'] = make_dict(s)
        if not current_app.config['custom_settings'].get('app_environment'):
            set_settings(app_name='Open Event', app_environment=app_environment)
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
    setting = Setting.query.order_by(desc(Setting.id)).first()
    if not setting:
        setting = Setting(**kwargs)
    else:
        for key, value in list(kwargs.items()):
            setattr(setting, key, value)
    from app.api.helpers.db import save_to_db

    save_to_db(setting, 'Setting saved')
    stripe.api_key = setting.stripe_secret_key

    if (
        setting.app_environment == Environment.DEVELOPMENT
        and not current_app.config['DEVELOPMENT']
    ):
        current_app.config.from_object('config.DevelopmentConfig')

    if (
        setting.app_environment == Environment.STAGING
        and not current_app.config['STAGING']
    ):
        current_app.config.from_object('config.StagingConfig')

    if (
        setting.app_environment == Environment.PRODUCTION
        and not current_app.config['PRODUCTION']
    ):
        current_app.config.from_object('config.ProductionConfig')

    if (
        setting.app_environment == Environment.TESTING
        and not current_app.config['TESTING']
    ):
        current_app.config.from_object('config.TestingConfig')

    current_app.config['custom_settings'] = make_dict(setting)


def make_dict(s):
    arguments = {}
    for name, column in list(s.__mapper__.columns.items()):
        if not (column.primary_key or column.unique):
            arguments[name] = getattr(s, name)
    return arguments

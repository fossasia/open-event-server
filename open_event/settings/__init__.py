from flask import current_app
from open_event.models.setting import Setting

from open_event.helpers.data_getter import DataGetter
from open_event.helpers.data import save_to_db


def get_settings():
    """
    Use this to get latest system settings
    """
    if 'custom_settings' in current_app.config:
        return current_app.config['custom_settings']
    s = DataGetter.get_system_setting()
    if s is None:
        set_settings(secret='My default secret')
        return current_app.config['custom_settings']
    else:
        current_app.config['custom_settings'] = s
        return s


def set_settings(**kwargs):
    """
    Update system settings
    """
    setting = Setting(**kwargs)
    save_to_db(setting, 'Setting saved')
    current_app.config['custom_settings'] = setting

from flask import current_app

from open_event.helpers.data_getter import DataGetter
from open_event.helpers.data import update_settings


def get_settings():
    """
    Use this to get latest system settings
    """
    if 'custom_settings' in current_app.config:
        return current_app.config['custom_settings']
    s = DataGetter.get_system_setting()
    if s is None:
        update_settings()
        return current_app.config['custom_settings']
    else:
        current_app.config['custom_settings'] = s
        return s

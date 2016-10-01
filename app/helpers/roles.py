from functools import wraps

from .data_getter import DataGetter
from enum import Enum
from flask import flash


class Role(Enum):
    any = "ANY"
    organizer = "ORGANIZER"
    volunteer = "VOLUNTEER"
    track_organizer = "TRACK_ORGANIZER"
    co_organizer = "CO_ORGANIZER"


def role_required(roles=(Role.any,)):
    def wrapper(decorated_function):
        @wraps(decorated_function)
        def decorated_view(*args, **kwargs):
            if can(roles, kwargs):
                return decorated_function(*args, **kwargs)
            return flash('Not permission')
        return decorated_view
    return wrapper


def can(roles, kwargs):
    event_id = kwargs.get('event_id', None)
    if event_id:
        for el in DataGetter.get_user_events_roles(event_id):
            if el.role in roles:
                return True
    return False

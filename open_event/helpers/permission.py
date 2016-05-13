from functools import wraps

from data_getter import DataGetter

ANY = "ANY"
ORGANIZER = "ORGANIZER"
VOLUNTEER = "VOLUNTEER"
TRACK_ORGANIZER = "TRACK_ORGANIZER"
CO_ORGANIZER = "CO_ORGANIZER"


def role_required(roles=(ANY,)):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if can(roles, kwargs):
                return fn(*args, **kwargs)
            return 'Not permission'
        return decorated_view
    return wrapper


def can(roles, kwargs):
    event_id = kwargs.get('event_id', None)
    if event_id:
        for el in DataGetter.get_user_events_roles(event_id):
            if el.role in roles:
                return True
    return False

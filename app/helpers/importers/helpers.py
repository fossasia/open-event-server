from datetime import timedelta, datetime

from app.helpers.data import save_to_db
from app.helpers.helpers import update_state
from app.models.role import Role
from app.models.user import ORGANIZER
from app.models.users_events_roles import UsersEventsRoles


def string_to_timedelta(string):
    if string:
        t = datetime.strptime(string, "%H:%M")
        return timedelta(hours=t.hour, minutes=t.minute, seconds=0)
    else:
        return timedelta(hours=0, minutes=0, seconds=0)


def update_status(task_handle, status):
    if task_handle and status:
        update_state(task_handle, status)


def own_event(event, user_id):
    role = Role.query.filter_by(name=ORGANIZER).first()
    uer = UsersEventsRoles(user_id=user_id, event=event, role=role)
    save_to_db(uer, 'UER saved')


def get_valid_event_name(value):
    name = None
    stop_words = ['ical', 'caldesc', 'calname', 'pentabarf']
    if value and value != '' and all(word not in value for word in stop_words):
        if '@' in value:
            splitted = value.split("@")
            name = splitted[len(splitted) - 1]
        else:
            name = value
    return name

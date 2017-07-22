from app.api.helpers.db import save_to_db
from app.models.activity import Activity, ACTIVITIES


def record_activity(template, login_user=None, **kwargs):
    """
    record an activity
    """
    if login_user:
        actor = login_user.email + ' (' + str(login_user.id) + ')'
    else:
        actor = 'Anonymous'
    id_str = ' (%d)'
    sequence = '"%s"'
    # add more information for objects
    for k in kwargs:
        v = kwargs[k]
        if k.find('_id') > -1:
            kwargs[k] = str(v)
        elif k.startswith('user'):
            kwargs[k] = sequence % v.email + id_str % v.id
        elif k.startswith('role'):
            kwargs[k] = sequence % v.title_name
        elif k.startswith('session'):
            kwargs[k] = sequence % v.title + id_str % v.id
        elif k.startswith('track'):
            kwargs[k] = sequence % v.name + id_str % v.id
        elif k.startswith('speaker'):
            kwargs[k] = sequence % v.name + id_str % v.id
        else:
            kwargs[k] = str(v)
    try:
        msg = ACTIVITIES[template].format(**kwargs)
    except Exception:  # in case some error happened, not good
        msg = '[ERROR LOGGING] %s' % template

    activity = Activity(actor=actor, action=msg)
    save_to_db(activity, 'Activity Recorded')

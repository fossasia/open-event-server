from flask.ext import login
from functools import wraps
from flask import url_for, redirect
from open_event.models.user import User


def is_super_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        if user.is_super_admin is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        if user.is_admin is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_organizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_organizer(event_id) is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_coorganizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_coorganizer(event_id) is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_track_organizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_track_organizer(event_id) is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_moderator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_moderator(event_id) is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function


def is_speaker(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_speaker(event_id) is False:
            return redirect(url_for('admin.forbidden_view'))
        return f(*args, **kwargs)

    return decorated_function

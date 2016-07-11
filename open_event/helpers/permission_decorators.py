from flask.ext import login
from functools import wraps
from flask import url_for, redirect, request
from flask.ext.restplus import abort

from open_event.models.user import User
from open_event.models.session import Session
from open_event.models.microlocation import Microlocation
from open_event.models.track import Track
from open_event.models.speaker import Speaker
from open_event.models.sponsor import Sponsor


def is_super_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        if user.is_super_admin is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_admin(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        if user.is_admin is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_organizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_staff is True:
            return f(*args, **kwargs)
        if user.is_organizer(event_id) is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_coorganizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_staff is True:
            return f(*args, **kwargs)
        if user.is_coorganizer(event_id) is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_track_organizer(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_staff is True:
            return f(*args, **kwargs)
        if user.is_track_organizer(event_id) is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def is_moderator(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_staff is True:
            return f(*args, **kwargs)
        if user.is_moderator(event_id) is False:
            abort(403)
        return f(*args, **kwargs)

    return decorated_function


def can_accept_and_reject(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        if user.is_staff is True:
            return f(*args, **kwargs)
        if user.is_organizer(event_id) is True or user.is_coorganizer(event_id) is True:
            return f(*args, **kwargs)
        abort(403)

    return decorated_function


def can_access(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = User.query.get(login.current_user.id)
        event_id = kwargs['event_id']
        url = request.url
        if user.is_staff is True:
            return f(*args, **kwargs)
        if 'events/' + event_id + '/' in url:
            if user.is_organizer(event_id) is True or user.is_track_organizer(event_id) is True or user.is_coorganizer(event_id) is True:
                return f(*args, **kwargs)
            abort(403)
        if '/create/' in url or '/new/' in url:
            if '/events/create/' in url:
                return f(*args, **kwargs)
            if 'session' in url:
                if user.can_create(Session, event_id) is True:
                    return f(*args, **kwargs)
            if 'track' in url:
                if user.can_create(Track, event_id) is True:
                    return f(*args, **kwargs)
            if 'speaker' in url:
                if user.can_create(Speaker, event_id) is True:
                    return f(*args, **kwargs)
            if 'sponsor' in url:
                if user.can_create(Sponsor, event_id) is True:
                    return f(*args, **kwargs)
            if 'microlocation' in url:
                if user.can_create(Microlocation, event_id) is True:
                    return f(*args, **kwargs)
            abort(403)
        if '/edit/' in url:
            if 'events/' + event_id + '/edit/' in url:
                if user.is_organizer(event_id) is True or user.is_coorganizer(event_id) is True:
                    return f(*args, **kwargs)
            if 'session' in url:
                if user.can_update(Session, event_id) is True:
                    return f(*args, **kwargs)
            if 'track' in url:
                if user.can_update(Track, event_id) is True:
                    return f(*args, **kwargs)
            if 'speaker' in url:
                if user.can_update(Speaker, event_id) is True:
                    return f(*args, **kwargs)
            if 'sponsor' in url:
                if user.can_update(Sponsor, event_id) is True:
                    return f(*args, **kwargs)
            if 'microlocation' in url:
                if user.can_update(Microlocation, event_id) is True:
                    return f(*args, **kwargs)
            abort(403)
        if '/delete/' in url or '/trash/' in url:
            if 'events/' + event_id + '/delete/' in url:
                if user.is_organizer(event_id) is True or user.is_coorganizer(event_id) is True:
                    return f(*args, **kwargs)
            if 'events/' + event_id + '/trash/' in url:
                if user.is_organizer(event_id) is True or user.is_coorganizer(event_id) is True:
                    return f(*args, **kwargs)
            if 'session' in url:
                if user.can_delete(Session, event_id) is True:
                    return f(*args, **kwargs)
            if 'track' in url:
                if user.can_delete(Track, event_id) is True:
                    return f(*args, **kwargs)
            if 'speaker' in url:
                if user.can_delete(Speaker, event_id) is True:
                    return f(*args, **kwargs)
            if 'sponsor' in url:
                if user.can_delete(Sponsor, event_id) is True:
                    return f(*args, **kwargs)
            if 'microlocation' in url:
                if user.can_delete(Microlocation, event_id) is True:
                    return f(*args, **kwargs)
            abort(403)

    return decorated_function

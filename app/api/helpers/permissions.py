from functools import wraps
from flask import current_app as app
from flask_jwt import _jwt_required, current_identity

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from flask import request
from datetime import datetime


def second_order_decorator(inner_dec):
    """
    Second order decorator. Decorator to apply on a decorator.
    https://stackoverflow.com/questions/5952641/decorating-decorators-try-to-get-my-head-around-understanding-it
    :param inner_dec:
    :return:
    """

    def ddmain(outer_dec):
        def decwrapper(f):
            wrapped = inner_dec(outer_dec(f))

            def fwrapper(*args, **kwargs):
                return wrapped(*args, **kwargs)

            return fwrapper

        return decwrapper

    return ddmain


def jwt_required(fn, realm=None):
    """
    Modified from original jwt_required to comply with `flask-rest-jsonapi` decorator conventions
    View decorator that requires a valid JWT token to be present in the request
    :param fn: function to be decorated
    :param realm: an optional realm
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        _jwt_required(realm or app.config['JWT_DEFAULT_REALM'])
        current_identity.last_accessed_at = datetime.utcnow()
        save_to_db(current_identity)
        return fn(*args, **kwargs)

    return decorator


@second_order_decorator(jwt_required)
def is_super_admin(f):
    """
    Decorator function for things allowed exclusively to super admin.
    Do not use this if the resource is also accessible by a normal admin, use the is_admin decorator instead.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity
        if not user.is_super_admin:
            return ForbiddenError({'source': ''}, 'Super admin access is required').respond()
        return f(*args, **kwargs)

    return decorated_function


@second_order_decorator(jwt_required)
def is_admin(f):
    """
    Decorator function for things allowed to admins and super admins.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity
        if not user.is_admin and not user.is_super_admin:
            return ForbiddenError({'source': ''}, 'Admin access is required').respond()
        return f(*args, **kwargs)

    return decorated_function


@second_order_decorator(jwt_required)
def is_user_itself(f):
    """
    Allows admin and super admin access to any resource irrespective of id.
    Otherwise the user can only access his/her resource.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity
        if not user.is_admin and not user.is_super_admin and user.id != kwargs['id']:
            return ForbiddenError({'source': ''}, 'Access Forbidden').respond()
        return f(*args, **kwargs)

    return decorated_function


@second_order_decorator(jwt_required)
def is_organizer(f):
    """
    Allows only Organizer to access the event resources.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and user.is_organizer(kwargs['event_id']):
            return f(*args, **kwargs)
        return ForbiddenError({'source': ''}, 'Organizer access is required').respond()

    return decorated_function


@second_order_decorator(jwt_required)
def is_coorganizer(f):
    """
    Allows Organizer and Co-organizer to access the event resources.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
                user.is_coorganizer(kwargs['event_id']) or
                user.is_organizer(kwargs['event_id'])):
            return f(*args, **kwargs)
        return ForbiddenError({'source': ''}, 'Co-organizer access is required.').respond()

    return decorated_function


@second_order_decorator(jwt_required)
def is_registrar(f):
    """
    Allows Organizer, Co-organizer and registrar to access the event resources.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
                    user.is_registrar(kwargs['event_id']) or
                    user.is_organizer(kwargs['event_id']) or
                user.is_coorganizer(kwargs['event_id'])):
            return f(*args, **kwargs)
        return ForbiddenError({'source': ''}, 'Registrar Access is Required.').respond()

    return decorated_function


@second_order_decorator(jwt_required)
def is_track_organizer(f):
    """
    Allows Organizer, Co-organizer and Track Organizer to access the resource(s).
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
                    user.is_track_organizer(kwargs['event_id']) or
                    user.is_organizer(kwargs['event_id']) or
                user.is_coorganizer(kwargs['event_id'])):
            return f(*args, **kwargs)
        return ForbiddenError({'source': ''}, 'Track Organizer access is Required.').respond()

    return decorated_function


@second_order_decorator(jwt_required)
def is_moderator(f):
    """
    Allows Organizer, Co-organizer and Moderator to access the resource(s).
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
                    user.is_moderator(kwargs['event_id']) or
                    user.is_organizer(kwargs['event_id']) or
                user.is_coorganizer(kwargs['event_id'])):
            return f(*args, **kwargs)
        return ForbiddenError({'source': ''}, 'Moderator Access is Required.').respond()

    return decorated_function


@second_order_decorator(jwt_required)
def accessible_events(f):
    """
    Filter the accessible events to the current authorized user
    If the user is not admin then only events created by user is
    accessible.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_identity
        if 'POST' in request.method:
            kwargs['user_id'] = user.id
        else:
            if not user.is_staff:
                kwargs['user_id'] = user.id

        return f(*args, **kwargs)

    return decorated_function

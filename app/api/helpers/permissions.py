from datetime import datetime
from functools import wraps

from flask import request
from flask_jwt_extended import current_user, verify_jwt_in_request

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from app.models import db
from app.models.event import Event


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

            fwrapper.__name__ = f.__name__

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
        verify_jwt_in_request()
        current_user.last_accessed_at = datetime.now()
        save_to_db(current_user)
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
        user = current_user
        if not user.is_super_admin:
            raise ForbiddenError({'source': ''}, 'Super admin access is required')
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
        user = current_user
        if not user.is_admin and not user.is_super_admin:
            raise ForbiddenError({'source': ''}, 'Admin access is required')
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
        user = current_user
        if not user.is_admin and not user.is_super_admin and user.id != kwargs['id']:
            raise ForbiddenError({'source': ''}, 'Access Forbidden')
        return f(*args, **kwargs)

    return decorated_function


@second_order_decorator(jwt_required)
def is_owner(f):
    """
    Allows only Owner to access the event resources.
    :param f:
    :return:
    """

    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = current_user

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and user.is_owner(kwargs['event_id']):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Owner access is required')

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
        user = current_user

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and user.is_organizer(kwargs['event_id']):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Organizer access is required')

    return decorated_function


def to_event_id(func):
    """
    Change event_identifier to event_id in kwargs
    :param f:
    :return:
    """

    @wraps(func)
    def decorated_function(*args, **kwargs):

        if 'event_identifier' in kwargs:
            if not kwargs['event_identifier'].isdigit():
                event = (
                    db.session.query(Event)
                    .filter_by(identifier=kwargs['event_identifier'])
                    .first()
                )
                kwargs['event_id'] = event.id
            else:
                kwargs['event_id'] = kwargs['event_identifier']
            kwargs.pop('event_identifier', None)
        return func(*args, **kwargs)

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
        user = current_user

        if user.is_staff or (
            'event_id' in kwargs and user.has_event_access(kwargs['event_id'])
        ):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Co-organizer access is required.')

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
        user = current_user

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
            user.is_registrar(kwargs['event_id'])
            or user.has_event_access(kwargs['event_id'])
        ):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Registrar Access is Required.')

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
        user = current_user

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
            user.is_track_organizer(kwargs['event_id'])
            or user.has_event_access(kwargs['event_id'])
        ):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Track Organizer access is Required.')

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
        user = current_user

        if user.is_staff:
            return f(*args, **kwargs)
        if 'event_id' in kwargs and (
            user.is_moderator(kwargs['event_id'])
            or user.has_event_access(kwargs['event_id'])
        ):
            return f(*args, **kwargs)
        raise ForbiddenError({'source': ''}, 'Moderator Access is Required.')

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
        user = current_user
        if 'POST' in request.method:
            kwargs['user_id'] = user.id
        else:
            if not user.is_staff:
                kwargs['user_id'] = user.id

        return f(*args, **kwargs)

    return decorated_function

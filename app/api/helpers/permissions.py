from functools import wraps
from flask import current_app as app
from flask_jwt import _jwt_required, current_identity
from app.api.helpers.errors import ForbiddenError


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
    :param realm: an optional realm
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        _jwt_required(realm or app.config['JWT_DEFAULT_REALM'])
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




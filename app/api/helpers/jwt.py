from flask import current_app
from flask.ext.scrypt import check_password_hash
from flask_jwt import _jwt_required
from app.models.user import User
from functools import wraps


def jwt_authenticate(email, password):
    """
    helper function to authenticate user if credentials are correct
    :param email:
    :param password:
    :return:
    """
    user = User.query.filter_by(email=email).first()
    if user is None:
        return None
    auth_ok = check_password_hash(
        password.encode('utf-8'),
        user.password.encode('utf-8'),
        user.salt
    )
    if auth_ok:
        return user
    else:
        return None


def jwt_identity(payload):
    """
    Jwt helper function
    :param payload:
    :return:
    """
    return User.query.get(payload['identity'])


def jwt_required(fn, realm=None):
    """
    Modified from original jwt_required to comply with `flask-rest-jsonapi` decorator conventions
    View decorator that requires a valid JWT token to be present in the request
    :param realm: an optional realm
    """
    @wraps(fn)
    def decorator(*args, **kwargs):
        _jwt_required(realm or current_app.config['JWT_DEFAULT_REALM'])
        return fn(*args, **kwargs)
    return decorator

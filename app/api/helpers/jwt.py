from flask import _app_ctx_stack as ctx_stack  # pytype: disable=import-error
from flask_jwt_extended.config import config
from flask_jwt_extended.exceptions import JWTExtendedException, UserLoadError
from flask_jwt_extended.view_decorators import _decode_jwt_from_request, _load_user
from jwt.exceptions import PyJWTError

from app.models.user import User


def jwt_authenticate(email, password):
    """
    helper function to authenticate user if credentials are correct
    :param email:
    :param password:
    :return:
    """
    user = User.query.filter_by(email=email.strip(), deleted_at=None).first()
    if user is None:
        return None
    auth_ok = user.facebook_login_hash == password or user.is_correct_password(password)
    if auth_ok:
        return user
    return None


def jwt_user_loader(identity):
    return User.query.filter_by(id=identity, deleted_at=None).first()


def get_identity():
    """
    To be used only if identity for expired tokens is required, otherwise use current_identity from flask_jwt
    :return:
    """
    token = None
    try:
        token, _ = _decode_jwt_from_request('access')
    except (JWTExtendedException, PyJWTError):
        token = getattr(ctx_stack.top, 'expired_jwt', None)

    if token:
        try:
            _load_user(token[config.identity_claim_key])
            return getattr(ctx_stack.top, 'jwt_user', None)
        except UserLoadError:
            pass

from flask_jwt_extended.exceptions import JWTExtendedException
from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

from app.api.helpers.jwt import get_identity


def rate_limit_key():
    user = None
    try:
        user = get_identity()
    except JWTExtendedException:
        user = None

    if user and getattr(user, 'id', None):
        return f'user:{user.id}'

    return get_ipaddr()


limiter = Limiter(key_func=rate_limit_key)


def init_app(app):
    default_limits = app.config.get('RATE_LIMIT_DEFAULTS', [])
    if default_limits:
        limiter.default_limits = default_limits
    limiter.init_app(app)

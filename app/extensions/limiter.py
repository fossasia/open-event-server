from flask_limiter import Limiter
from flask_limiter.util import get_ipaddr

limiter = Limiter(key_func=get_ipaddr)


def init_app(app):
    limiter.init_app(app)

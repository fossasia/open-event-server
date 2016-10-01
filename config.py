"""Written by - Rafal Kowalski"""
import os

_basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    SERVER_NAME = os.getenv('SERVER_NAME')
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ERROR_404_HELP = False
    CACHING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../app.db')
    BASE_DIR = _basedir


class ProductionConfig(Config):
    DEBUG = False
    MINIFY_PAGE = True
    PRODUCTION = True
    INTEGRATE_SOCKETIO = True

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 0.1

    # if force off
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    if socketio_integration == 'false':
        INTEGRATE_SOCKETIO = False
    # you don't want production on default db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    if not SQLALCHEMY_DATABASE_URI:
        print('`DATABASE_URL` either not exported or empty')


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    MINIFY_PAGE = False

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 0.1

    # If Env Var `INTEGRATE_SOCKETIO` is set to 'true', then integrate SocketIO
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    INTEGRATE_SOCKETIO = bool(socketio_integration == 'true')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    if not SQLALCHEMY_DATABASE_URI:
        print('`DATABASE_URL` either not exported or empty')


class TestingConfig(Config):
    TESTING = True
    CACHING = False
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True


class LocalPSQLConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:start@localhost/test"


class LocalSQLITEConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(_basedir, 'app.db')

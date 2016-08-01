"""Written by - Rafal Kowalski"""
import os

_basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
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
    # you don't want production on default db
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    if not SQLALCHEMY_DATABASE_URI:
        print '`DATABASE_URL` either not exported or empty'


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    MINIFY_PAGE = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    if not SQLALCHEMY_DATABASE_URI:
        print '`DATABASE_URL` either not exported or empty'


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

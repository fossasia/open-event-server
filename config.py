# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

VERSION_NAME = '1.0.0-alpha.3'

# available languages
LANGUAGES = {
    'en': 'English',
    'bn': 'Bengali/Bangla',
    'zh_Hans': 'Chinese (Simplified)',
    'zh_Hant': 'Chinese (Traditional)',
    'fr': 'French',
    'de': 'German',
    'id': 'Indonesian',
    'ko': 'Korean',
    'pl': 'Polish',
    'es': 'Spanish',
    'th': 'Thai',
    'vi': 'Vietnamese',
    'hi': 'Hindi',
    'ja': 'Japanese',
    'ru': 'Russian',
}


class Config(object):
    VERSION = VERSION_NAME
    DEBUG = False
    TESTING = False
    CSRF_ENABLED = True
    PROFILE = False
    SERVER_NAME = os.getenv('SERVER_NAME')
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ERROR_404_HELP = False
    CACHING = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../app.db')
    BASE_DIR = basedir
    FORCE_SSL = os.getenv('FORCE_SSL', 'no') == 'yes'
    SQLALCHEMY_RECORD_QUERIES = False

    UPLOADS_FOLDER = BASE_DIR + '/static/uploads/'
    TEMP_UPLOADS_FOLDER = BASE_DIR + '/static/uploads/temp/'
    UPLOAD_FOLDER = UPLOADS_FOLDER
    STATIC_URL = '/static/'
    STATIC_ROOT = 'staticfiles'
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

    if FORCE_SSL:
        PREFERRED_URL_SCHEME = 'https'


class ProductionConfig(Config):
    DEBUG = False
    MINIFY_PAGE = True
    PRODUCTION = True
    INTEGRATE_SOCKETIO = True

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = False
    DATABASE_QUERY_TIMEOUT = 0.1

    # if force off
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    if socketio_integration == 'false':
        INTEGRATE_SOCKETIO = False
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

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = True
    DATABASE_QUERY_TIMEOUT = 0.1

    # If Env Var `INTEGRATE_SOCKETIO` is set to 'true', then integrate SocketIO
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    INTEGRATE_SOCKETIO = bool(socketio_integration == 'true')

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', '')
    if not SQLALCHEMY_DATABASE_URI:
        print '`DATABASE_URL` either not exported or empty'


class TestingConfig(Config):
    TESTING = True
    CACHING = False
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    SQLALCHEMY_RECORD_QUERIES = True


class LocalPSQLConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:start@localhost/test"


class LocalSQLITEConfig(Config):
    DEVELOPMENT = True
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')

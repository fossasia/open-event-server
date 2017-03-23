# -*- coding: utf-8 -*-
import os

basedir = os.path.abspath(os.path.dirname(__file__))

VERSION_NAME = '1.0.0-alpha.10'

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
    """
    The base configuration option. Contains the defaults.
    """

    DEBUG = False

    DEVELOPMENT = False
    STAGING = False
    PRODUCTION = False
    TESTING = False

    CACHING = False
    PROFILE = False
    SQLALCHEMY_RECORD_QUERIES = False
    INTEGRATE_SOCKETIO = False

    VERSION = VERSION_NAME
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ERROR_404_HELP = False
    CSRF_ENABLED = True
    SERVER_NAME = os.getenv('SERVER_NAME')
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', None)
    DATABASE_QUERY_TIMEOUT = 0.1

    if not SQLALCHEMY_DATABASE_URI:
        print '`DATABASE_URL` either not exported or empty'
        exit()

    BASE_DIR = basedir
    FORCE_SSL = os.getenv('FORCE_SSL', 'no') == 'yes'

    UPLOADS_FOLDER = BASE_DIR + '/static/uploads/'
    TEMP_UPLOADS_FOLDER = BASE_DIR + '/static/uploads/temp/'
    UPLOAD_FOLDER = UPLOADS_FOLDER
    STATIC_URL = '/static/'
    STATIC_ROOT = 'staticfiles'
    STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

    if FORCE_SSL:
        PREFERRED_URL_SCHEME = 'https'


class ProductionConfig(Config):
    """
    The configuration for a production environment
    """

    MINIFY_PAGE = True
    PRODUCTION = True
    INTEGRATE_SOCKETIO = True
    CACHING = True

    # if force off
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    if socketio_integration == 'false':
        INTEGRATE_SOCKETIO = False


class StagingConfig(ProductionConfig):
    """
    The configuration for a staging environment
    """

    PRODUCTION = False
    STAGING = True


class DevelopmentConfig(Config):
    """
    The configuration for a development environment
    """

    DEVELOPMENT = True
    DEBUG = True
    CACHING = True

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = True

    # If Env Var `INTEGRATE_SOCKETIO` is set to 'true', then integrate SocketIO
    socketio_integration = os.environ.get('INTEGRATE_SOCKETIO')
    INTEGRATE_SOCKETIO = bool(socketio_integration == 'true')


class TestingConfig(Config):
    """
    The configuration for a test suit
    """
    INTEGRATE_SOCKETIO = False
    TESTING = True
    CELERY_ALWAYS_EAGER = True
    CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_ENABLED = False
    BROKER_BACKEND = 'memory'

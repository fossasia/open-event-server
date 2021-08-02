import os
import sys

from envparse import env

env.read_envfile()

basedir = os.path.abspath(os.path.dirname(__file__))

VERSION_NAME = '1.19.1'

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


class Config:
    """
    The base configuration option. Contains the defaults.
    """

    DEBUG = False

    DEVELOPMENT = False
    STAGING = False
    PRODUCTION = False
    TESTING = False

    SECRET_KEY = env.str('SECRET_KEY', default=None)

    CACHING = False
    PROFILE = False
    SQLALCHEMY_RECORD_QUERIES = False

    FLASK_ADMIN_SWATCH = 'lumen'

    VERSION = VERSION_NAME
    ACCEPTED_LANGUAGES = [
        'en',
        'bn',
        'de',
        'es',
        'fr',
        'hi',
        'id',
        'ja',
        'ko',
        'pl',
        'ru',
        'th',
        'vi',
        'zh_Hans',
        'zh_Hant',
    ]
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    ERROR_404_HELP = False
    CSRF_ENABLED = True
    SERVER_NAME = env('SERVER_NAME', default=None)
    CORS_HEADERS = 'Content-Type'
    SQLALCHEMY_DATABASE_URI = env('DATABASE_URL', default=None)
    SQLALCHEMY_ENGINE_OPTIONS = {'pool_pre_ping': True}
    SERVE_STATIC = env.bool('SERVE_STATIC', default=False)
    DATABASE_QUERY_TIMEOUT = 0.1
    SENTRY_DSN = env('SENTRY_DSN', default=None)
    SENTRY_RELEASE_NAME = (
        env('SENTRY_PROJECT_NAME', default='eventyay-server') + '@' + VERSION_NAME
    )
    SENTRY_TRACES_SAMPLE_RATE = env.float('SENTRY_TRACES_SAMPLE_RATE', default=0.1)
    ENABLE_ELASTICSEARCH = env.bool('ENABLE_ELASTICSEARCH', default=False)
    ELASTICSEARCH_HOST = env('ELASTICSEARCH_HOST', default='localhost:9200')
    REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')
    CELERY_BACKKEND = env('CELERY_BACKEND', default='redis')

    # API configs
    SOFT_DELETE = True
    PROPOGATE_ERROR = env.bool('PROPOGATE_ERROR', default=False)
    DASHERIZE_API = True
    API_PROPOGATE_UNCAUGHT_EXCEPTIONS = env.bool(
        'API_PROPOGATE_UNCAUGHT_EXCEPTIONS', default=True
    )
    ETAG = True
    ATTACH_ORDER_PDF = env.bool('ATTACH_ORDER_PDF', default=True)
    # Allow unverified users to buy free tickets. Default: False
    ALLOW_UNVERIFIED_FREE_ORDERS = env.bool('ALLOW_UNVERIFIED_FREE_ORDERS', default=False)

    if not SQLALCHEMY_DATABASE_URI:
        print('`DATABASE_URL` either not exported or empty')
        sys.exit()

    BASE_DIR = basedir
    FORCE_SSL = os.getenv('FORCE_SSL', 'no') == 'yes'

    if SERVE_STATIC:
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

    ENV = 'production'
    MINIFY_PAGE = True
    PRODUCTION = True
    CACHING = True


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

    ENV = 'development'
    DEVELOPMENT = True
    DEBUG = True
    CACHING = True
    PROPOGATE_ERROR = True

    # Test database performance
    SQLALCHEMY_RECORD_QUERIES = True


class TestingConfig(Config):
    """
    The configuration for a test suit
    """

    ENV = 'testing'
    TESTING = True
    CELERY_TASK_ALWAYS_EAGER = True
    CELERY_TASK_EAGER_PROPAGATES = True
    SQLALCHEMY_RECORD_QUERIES = True
    DEBUG_TB_ENABLED = False
    BROKER_BACKEND = 'memory'
    SQLALCHEMY_DATABASE_URI = env('TEST_DATABASE_URL', default=None)
    PROPOGATE_ERROR = True

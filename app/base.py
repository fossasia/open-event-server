import sys
import logging
import secrets
from pathlib import Path
from datetime import timedelta

from flask import Flask
from envparse import env

from .api.helpers.mail_recorder import MailRecorder
from .models.utils import sqlite_datetime_fix


FOLDER = Path(__file__).parent

static_dir = FOLDER.parent / '/static'
template_dir = FOLDER / 'templates'
app = Flask(__name__, static_folder=str(static_dir), template_folder=str(template_dir))

env.read_envfile()
app.config.from_object(env('APP_CONFIG', default='config.ProductionConfig'))
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
app.config['JWT_HEADER_TYPE'] = 'JWT'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=365)
app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
app.config['JWT_REFRESH_COOKIE_PATH'] = '/v1/auth/token/refresh'
app.config['JWT_SESSION_COOKIE'] = False
app.config['JWT_BLACKLIST_ENABLED'] = True
app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['refresh']
# setup celery
app.config['broker_url'] = app.config['REDIS_URL']
app.config['result_backend'] = app.config['broker_url']
app.config['accept_content'] = ['json', 'application/text']

app.config['MAIL_RECORDER'] = MailRecorder(use_env=True)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

if not app.config['SECRET_KEY']:
    if app.config['PRODUCTION']:
        app.logger.error(
            'SECRET_KEY must be set in .env or environment variables in production'
        )
        exit(1)
    else:
        random_secret = secrets.token_hex()
        app.logger.warning(
            'Using random secret "%s" for development server. '
            'This is NOT recommended. '
            'Set proper SECRET_KEY in .env or environment variables',
            random_secret
        )
        app.config['SECRET_KEY'] = random_secret


if app.config[  # pytype: disable=attribute-error
    'SQLALCHEMY_DATABASE_URI'
].startswith("sqlite://"):
    sqlite_datetime_fix()

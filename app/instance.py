import logging
import os.path
import secrets
import sys
from datetime import timedelta

import sentry_sdk
import sqlalchemy as sa
import stripe
from celery.signals import after_task_publish
from flask_babel import Babel
from envparse import env
from flask import Flask, json, make_response, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_login import current_user
from flask_migrate import Migrate
from healthcheck import HealthCheck
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.flask import FlaskIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from werkzeug.middleware.profiler import ProfilerMiddleware

from app.api import routes  # noqa: Used for registering routes
from app.api.custom.check_in_stats import check_in_stats_routes
from app.api.helpers.auth import AuthManager, is_token_blacklisted
from app.api.helpers.cache import cache
from app.api.helpers.errors import ErrorResponse
from app.api.helpers.jwt import jwt_user_loader
from app.api.helpers.mail_recorder import MailRecorder
from app.extensions import limiter, shell
from app.models import db
from app.models.utils import add_engine_pidguard, sqlite_datetime_fix
from app.templates.flask_ext.jinja.filters import init_filters
from app.views.blueprints import BlueprintsManager
from app.views.healthcheck import (
    health_check_celery,
    health_check_db,
    health_check_migrations,
)
from app.views.redis_store import redis_store
from app.graphql import views as graphql_views

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

static_dir = os.path.dirname(os.path.dirname(__file__)) + "/static"
template_dir = os.path.dirname(__file__) + "/templates"
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
env.read_envfile()


class ReverseProxied:
    """
    ReverseProxied flask wsgi app wrapper from http://stackoverflow.com/a/37842465/1562480 by aldel
    """

    def __init__(self, wsgi_app):
        self.app = wsgi_app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        if os.getenv('FORCE_SSL', 'no') == 'yes':
            environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)


app.wsgi_app = ReverseProxied(app.wsgi_app)

app_created = False


def create_app():
    global app_created
    if not app_created:
        BlueprintsManager.register(app)
        graphql_views.init_app(app)
    Migrate(app, db)

    app.config.from_object(env('APP_CONFIG', default='config.ProductionConfig'))

    if not app.config['SECRET_KEY']:
        if app.config['PRODUCTION']:
            app.logger.error(
                'SECRET_KEY must be set in .env or environment variables in production'
            )
            exit(1)
        else:
            random_secret = secrets.token_hex()
            app.logger.warning(
                f'Using random secret "{ random_secret }" for development server. '
                'This is NOT recommended. Set proper SECRET_KEY in .env or environment variables'
            )
            app.config['SECRET_KEY'] = random_secret

    db.init_app(app)

    if app.config['CACHING']:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache.init_app(app, config={'CACHE_TYPE': 'null'})

    stripe.api_key = 'SomeStripeKey'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    # set up jwt
    app.config['JWT_HEADER_TYPE'] = 'JWT'
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=365)
    app.config['JWT_ERROR_MESSAGE_KEY'] = 'error'
    app.config['JWT_TOKEN_LOCATION'] = ['cookies', 'headers']
    app.config['JWT_REFRESH_COOKIE_PATH'] = '/v1/auth/token/refresh'
    app.config['JWT_SESSION_COOKIE'] = False
    app.config['JWT_BLACKLIST_ENABLED'] = True
    app.config['JWT_BLACKLIST_TOKEN_CHECKS'] = ['refresh']
    _jwt = JWTManager(app)
    _jwt.user_loader_callback_loader(jwt_user_loader)
    _jwt.token_in_blacklist_loader(is_token_blacklisted)

    # setup celery
    app.config['broker_url'] = app.config['REDIS_URL']
    app.config['result_backend'] = app.config['broker_url']
    app.config['accept_content'] = ['json', 'application/text']

    app.config['MAIL_RECORDER'] = MailRecorder(use_env=True)

    CORS(app, resources={r"/*": {"origins": "*"}})
    AuthManager.init_login(app)

    if app.config['TESTING'] and app.config['PROFILE']:
        # Profiling
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # development api
    with app.app_context():
        from app.api.admin_statistics_api.events import event_statistics
        from app.api.auth import auth_routes
        from app.api.custom.attendees import attendee_blueprint
        from app.api.bootstrap import api_v1
        from app.api.celery_tasks import celery_routes
        from app.api.event_copy import event_copy
        from app.api.exports import export_routes
        from app.api.imports import import_routes
        from app.api.uploads import upload_routes
        from app.api.users import user_misc_routes
        from app.api.orders import order_misc_routes
        from app.api.role_invites import role_invites_misc_routes
        from app.api.speaker_invites import speaker_invites_misc_routes
        from app.api.auth import authorised_blueprint
        from app.api.admin_translations import admin_blueprint
        from app.api.orders import alipay_blueprint, stripe_blueprint
        from app.api.sessions import sessions_blueprint
        from app.api.settings import admin_misc_routes
        from app.api.server_version import info_route
        from app.api.custom.orders import ticket_blueprint
        from app.api.custom.orders import order_blueprint
        from app.api.custom.invoices import event_blueprint
        from app.api.custom.calendars import calendar_routes
        from app.api.tickets import tickets_routes
        from app.api.custom.role_invites import role_invites_routes
        from app.api.custom.users_groups_roles import users_groups_roles_routes
        from app.api.custom.events import events_routes
        from app.api.custom.groups import groups_routes
        from app.api.custom.group_role_invite import group_role_invites_routes
        from app.api.video_stream import streams_routes
        from app.api.events import events_blueprint
        from app.api.custom.badge_forms import badge_forms_routes
        from app.api.custom.tickets import ticket_routes
        from app.api.custom.users import users_routes
        from app.api.custom.users_check_in import users_check_in_routes

        app.register_blueprint(api_v1)
        app.register_blueprint(event_copy)
        app.register_blueprint(upload_routes)
        app.register_blueprint(export_routes)
        app.register_blueprint(import_routes)
        app.register_blueprint(celery_routes)
        app.register_blueprint(auth_routes)
        app.register_blueprint(event_statistics)
        app.register_blueprint(user_misc_routes)
        app.register_blueprint(attendee_blueprint)
        app.register_blueprint(order_misc_routes)
        app.register_blueprint(role_invites_misc_routes)
        app.register_blueprint(speaker_invites_misc_routes)
        app.register_blueprint(authorised_blueprint)
        app.register_blueprint(admin_blueprint)
        app.register_blueprint(alipay_blueprint)
        app.register_blueprint(stripe_blueprint)
        app.register_blueprint(admin_misc_routes)
        app.register_blueprint(info_route)
        app.register_blueprint(ticket_blueprint)
        app.register_blueprint(order_blueprint)
        app.register_blueprint(event_blueprint)
        app.register_blueprint(sessions_blueprint)
        app.register_blueprint(calendar_routes)
        app.register_blueprint(streams_routes)
        app.register_blueprint(role_invites_routes)
        app.register_blueprint(users_groups_roles_routes)
        app.register_blueprint(events_routes)
        app.register_blueprint(groups_routes)
        app.register_blueprint(events_blueprint)
        app.register_blueprint(tickets_routes)
        app.register_blueprint(group_role_invites_routes)
        app.register_blueprint(badge_forms_routes)
        app.register_blueprint(ticket_routes)
        app.register_blueprint(users_routes)
        app.register_blueprint(check_in_stats_routes)
        app.register_blueprint(users_check_in_routes)

        add_engine_pidguard(db.engine)

        if app.config[  # pytype: disable=attribute-error
            'SQLALCHEMY_DATABASE_URI'
        ].startswith("sqlite://"):
            sqlite_datetime_fix()

    sa.orm.configure_mappers()

    if app.config['SERVE_STATIC']:
        app.add_url_rule(
            '/static/<path:filename>', endpoint='static', view_func=app.send_static_file
        )

    # sentry
    if not app_created and 'SENTRY_DSN' in app.config:
        sentry_sdk.init(
            app.config['SENTRY_DSN'],
            integrations=[
                FlaskIntegration(),
                RedisIntegration(),
                CeleryIntegration(),
                SqlalchemyIntegration(),
            ],
            release=app.config['SENTRY_RELEASE_NAME'],
            traces_sample_rate=app.config['SENTRY_TRACES_SAMPLE_RATE'],
        )

    # redis
    redis_store.init_app(app)

    # Initialize Extensions
    shell.init_app(app)
    limiter.init_app(app)

    app_created = True
    return app


current_app = create_app()
init_filters(app)

# Babel
babel = Babel(current_app)


@babel.localeselector
def get_locale():
    # Try to guess the language from the user accept
    # header the browser transmits. We support de/fr/en in this
    # example. The best match wins.
    # pytype: disable=mro-error
    return request.accept_languages.best_match(current_app.config['ACCEPTED_LANGUAGES'])
    # pytype: enable=mro-error


# http://stackoverflow.com/questions/26724623/
@app.before_request
def track_user():
    if current_user.is_authenticated:
        current_user.update_lat()


# Health-check
health = HealthCheck(current_app, "/health-check")
health.add_check(health_check_celery)
health.add_check(health_check_db)
health.add_check(health_check_migrations)


# register celery tasks. removing them will cause the tasks to not function. so don't remove them
# it is important to register them after celery is defined to resolve circular imports

from .api.helpers import tasks

celery = tasks.celery
# register scheduled jobs
from app.api.helpers.scheduled_jobs import setup_scheduled_task

setup_scheduled_task(celery)


# http://stackoverflow.com/questions/9824172/find-out-whether-celery-task-exists
@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = celery.tasks.get(sender)
    backend = task.backend if task else celery.backend
    backend.store_result(headers['id'], None, 'WAITING')


@app.errorhandler(500)
def internal_server_error(error):
    if current_app.config['PROPOGATE_ERROR'] is True:
        exc = ErrorResponse(str(error))
    else:
        exc = ErrorResponse('Unknown error')
    return exc.respond()


@app.errorhandler(429)
def ratelimit_handler(error):
    return make_response(
        json.dumps({'status': 429, 'title': 'Request Limit Exceeded'}),
        429,
        {'Content-Type': 'application/vnd.api+json'},
    )


@app.errorhandler(ErrorResponse)
def handle_exception(error: ErrorResponse):
    return error.respond()


if __name__ == '__main__':
    current_app.run()

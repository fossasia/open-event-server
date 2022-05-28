import os.path

import sentry_sdk
import sqlalchemy as sa
import stripe
from celery.signals import after_task_publish
from flask_babel import Babel
from flask import json, make_response, request
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

from .api import routes  # noqa: Used for registering routes
from .api.helpers.auth import AuthManager, is_token_blacklisted
from .api.helpers.cache import cache
from .api.helpers.errors import ErrorResponse
from .api.helpers.jwt import jwt_user_loader
from .extensions import limiter, shell
from .models import db
from .models.utils import add_engine_pidguard
from .templates.flask_ext.jinja.filters import init_filters
from .views.blueprints import BlueprintsManager
from .views.healthcheck import (
    health_check_celery,
    health_check_db,
    health_check_migrations,
)
from .views.redis_store import redis_store
from .graphql import views as graphql_views

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class ReverseProxied:
    """
    ReverseProxied flask wsgi app wrapper from
    http://stackoverflow.com/a/37842465/1562480 by aldel
    """

    def __init__(self, an_app):
        self.app = an_app

    def __call__(self, environ, start_response):
        scheme = environ.get('HTTP_X_FORWARDED_PROTO')
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        if os.getenv('FORCE_SSL', 'no') == 'yes':
            environ['wsgi.url_scheme'] = 'https'
        return self.app(environ, start_response)


def create_app():
    from .base import app

    db.init_app(app)

    if app.config['CACHING']:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache.init_app(app, config={'CACHE_TYPE': 'null'})

    stripe.api_key = 'SomeStripeKey'

    # set up jwt
    _jwt = JWTManager(app)
    _jwt.user_loader_callback_loader(jwt_user_loader)
    _jwt.token_in_blacklist_loader(is_token_blacklisted)

    CORS(app, resources={r"/*": {"origins": "*"}})
    AuthManager.init_login(app)
    app.wsgi_app = ReverseProxied(app.wsgi_app)
    BlueprintsManager.register(app)
    graphql_views.init_app(app)
    Migrate(app, db)
    init_filters(app)

    # Babel
    babel = Babel(app)

    @babel.localeselector
    def get_locale():
        # Try to guess the language from the user accept
        # header the browser transmits. We support de/fr/en in this
        # example. The best match wins.
        # pytype: disable=mro-error
        return request.accept_languages.best_match(app.config['ACCEPTED_LANGUAGES'])
        # pytype: enable=mro-error

    if app.config['TESTING'] and app.config['PROFILE']:
        # Profiling
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # development api
    with app.app_context():
        from .api.admin_statistics_api.events import event_statistics
        from .api.auth import auth_routes
        from .api.custom.attendees import attendee_blueprint
        from .api.bootstrap import api_v1
        from .api.celery_tasks import celery_routes
        from .api.event_copy import event_copy
        from .api.exports import export_routes
        from .api.imports import import_routes
        from .api.uploads import upload_routes
        from .api.users import user_misc_routes
        from .api.orders import order_misc_routes
        from .api.role_invites import role_invites_misc_routes
        from .api.speaker_invites import speaker_invites_misc_routes
        from .api.auth import authorised_blueprint
        from .api.admin_translations import admin_blueprint
        from .api.orders import alipay_blueprint
        from .api.sessions import sessions_blueprint
        from .api.settings import admin_misc_routes
        from .api.server_version import info_route
        from .api.custom.orders import ticket_blueprint
        from .api.custom.orders import order_blueprint
        from .api.custom.invoices import event_blueprint
        from .api.custom.calendars import calendar_routes
        from .api.tickets import tickets_routes
        from .api.custom.role_invites import role_invites_routes
        from .api.custom.users_groups_roles import users_groups_roles_routes
        from .api.custom.events import events_routes
        from .api.custom.groups import groups_routes
        from .api.custom.group_role_invite import group_role_invites_routes
        from .api.video_stream import streams_routes
        from .api.events import events_blueprint

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

        add_engine_pidguard(db.engine)

    sa.orm.configure_mappers()

    if app.config['SERVE_STATIC']:
        app.add_url_rule(
            '/static/<path:filename>', endpoint='static', view_func=app.send_static_file
        )

    # sentry
    if 'SENTRY_DSN' in app.config:
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
    # Health-check
    health = HealthCheck(app, "/health-check")
    health.add_check(health_check_celery)
    health.add_check(health_check_db)
    health.add_check(health_check_migrations)

    # http://stackoverflow.com/questions/26724623/
    @app.before_request
    def track_user():
        if current_user.is_authenticated:
            current_user.update_lat()

    @app.errorhandler(500)
    def internal_server_error(error):
        if app.config['PROPOGATE_ERROR'] is True:
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

    return app


# register celery tasks. removing them will cause the tasks to not function. so don't
# remove them it is important to register them after celery is defined
# to resolve circular imports

from .api.helpers import tasks

celery = tasks.celery
# register scheduled jobs
from .api.helpers.scheduled_jobs import setup_scheduled_task

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


import app.cli  # noqa

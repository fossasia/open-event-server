from celery.signals import after_task_publish
import logging
import os.path
from envparse import env

import sys
from flask import Flask, json, make_response
from flask_celeryext import FlaskCeleryExt
from app.settings import get_settings, get_setts
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager
from flask_login import current_user
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from datetime import timedelta
from flask_cors import CORS
from flask_rest_jsonapi.errors import jsonapi_errors
from flask_rest_jsonapi.exceptions import JsonApiException
from healthcheck import HealthCheck
from apscheduler.schedulers.background import BackgroundScheduler
from elasticsearch_dsl.connections import connections
from pytz import utc

import sqlalchemy as sa

import stripe
from app.settings import get_settings
from app.models import db
from app.api.helpers.jwt import jwt_user_loader
from app.api.helpers.cache import cache
from werkzeug.middleware.profiler import ProfilerMiddleware
from app.views import BlueprintsManager
from app.api.helpers.auth import AuthManager, is_token_blacklisted
from app.api.helpers.scheduled_jobs import send_after_event_mail, send_event_fee_notification, \
    send_event_fee_notification_followup, change_session_state_on_event_completion, \
    expire_pending_tickets, send_monthly_event_invoice, event_invoices_mark_due
from app.models.event import Event
from app.models.role_invite import RoleInvite
from app.views.healthcheck import health_check_celery, health_check_db, health_check_migrations, check_migrations
from app.views.elastic_search import client
from app.views.elastic_cron_helpers import sync_events_elasticsearch, cron_rebuild_events_elasticsearch
from app.views.redis_store import redis_store
from app.views.celery_ import celery
from app.templates.flask_ext.jinja.filters import init_filters
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

static_dir = os.path.dirname(os.path.dirname(__file__)) + "/static"
template_dir = os.path.dirname(__file__) + "/templates"
app = Flask(__name__, static_folder=static_dir, template_folder=template_dir)
limiter = Limiter(app)
env.read_envfile()


class ReverseProxied(object):
    """
    ReverseProxied flask wsgi app wrapper from http://stackoverflow.com/a/37842465/1562480 by aldel
    """

    def __init__(self, app):
        self.app = app

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
    Migrate(app, db)

    app.config.from_object(env('APP_CONFIG', default='config.ProductionConfig'))
    db.init_app(app)
    _manager = Manager(app)
    _manager.add_command('db', MigrateCommand)

    if app.config['CACHING']:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache.init_app(app, config={'CACHE_TYPE': 'null'})

    stripe.api_key = 'SomeStripeKey'
    app.secret_key = 'super secret key'
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
    app.config['CELERY_BROKER_URL'] = app.config['REDIS_URL']
    app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']
    app.config['CELERY_ACCEPT_CONTENT'] = ['json', 'application/text']

    CORS(app, resources={r"/*": {"origins": "*"}})
    AuthManager.init_login(app)

    if app.config['TESTING'] and app.config['PROFILE']:
        # Profiling
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # development api
    with app.app_context():
        from app.api.admin_statistics_api.events import event_statistics
        from app.api.auth import auth_routes
        from app.api.attendees import attendee_misc_routes
        from app.api.bootstrap import api_v1
        from app.api.celery_tasks import celery_routes
        from app.api.event_copy import event_copy
        from app.api.exports import export_routes
        from app.api.imports import import_routes
        from app.api.uploads import upload_routes
        from app.api.users import user_misc_routes
        from app.api.orders import order_misc_routes
        from app.api.role_invites import role_invites_misc_routes
        from app.api.auth import ticket_blueprint, authorised_blueprint
        from app.api.admin_translations import admin_blueprint
        from app.api.orders import alipay_blueprint
        from app.api.settings import admin_misc_routes

        app.register_blueprint(api_v1)
        app.register_blueprint(event_copy)
        app.register_blueprint(upload_routes)
        app.register_blueprint(export_routes)
        app.register_blueprint(import_routes)
        app.register_blueprint(celery_routes)
        app.register_blueprint(auth_routes)
        app.register_blueprint(event_statistics)
        app.register_blueprint(user_misc_routes)
        app.register_blueprint(attendee_misc_routes)
        app.register_blueprint(order_misc_routes)
        app.register_blueprint(role_invites_misc_routes)
        app.register_blueprint(ticket_blueprint)
        app.register_blueprint(authorised_blueprint)
        app.register_blueprint(admin_blueprint)
        app.register_blueprint(alipay_blueprint)
        app.register_blueprint(admin_misc_routes)

    sa.orm.configure_mappers()

    if app.config['SERVE_STATIC']:
        app.add_url_rule('/static/<path:filename>',
                         endpoint='static',
                         view_func=app.send_static_file)

    # sentry
    if not app_created and 'SENTRY_DSN' in app.config:
        sentry_sdk.init(app.config['SENTRY_DSN'], integrations=[FlaskIntegration()])

    # redis
    redis_store.init_app(app)

    # elasticsearch
    if app.config['ENABLE_ELASTICSEARCH']:
        client.init_app(app)
        connections.add_connection('default', client.elasticsearch)
        with app.app_context():
            try:
                cron_rebuild_events_elasticsearch.delay()
            except Exception:
                pass

    app_created = True
    return app, _manager, db, _jwt


current_app, manager, database, jwt = create_app()
init_filters(app)


# http://stackoverflow.com/questions/26724623/
@app.before_request
def track_user():
    if current_user.is_authenticated:
        current_user.update_lat()


def make_celery(app=None):
    app = app or create_app()[0]
    celery.conf.update(app.config)
    ext = FlaskCeleryExt(app)
    return ext.celery


# Health-check
health = HealthCheck(current_app, "/health-check")
health.add_check(health_check_celery)
health.add_check(health_check_db)
with current_app.app_context():
    current_app.config['MIGRATION_STATUS'] = check_migrations()
health.add_check(health_check_migrations)


# http://stackoverflow.com/questions/9824172/find-out-whether-celery-task-exists
@after_task_publish.connect
def update_sent_state(sender=None, headers=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = celery.tasks.get(sender)
    backend = task.backend if task else celery.backend
    backend.store_result(headers['id'], None, 'WAITING')


# register celery tasks. removing them will cause the tasks to not function. so don't remove them
# it is important to register them after celery is defined to resolve circular imports

from .api.helpers import tasks

# import helpers.tasks


scheduler = BackgroundScheduler(timezone=utc)
# scheduler.add_job(send_mail_to_expired_orders, 'interval', hours=5)
# scheduler.add_job(empty_trash, 'cron', hour=5, minute=30)
if app.config['ENABLE_ELASTICSEARCH']:
    scheduler.add_job(sync_events_elasticsearch, 'interval', minutes=60)
    scheduler.add_job(cron_rebuild_events_elasticsearch, 'cron', day=7)

scheduler.add_job(send_after_event_mail, 'cron', hour=5, minute=30)
scheduler.add_job(send_event_fee_notification, 'cron', day=1)
scheduler.add_job(send_event_fee_notification_followup, 'cron', day=1, month='1-12')
scheduler.add_job(change_session_state_on_event_completion, 'cron', hour=5, minute=30)
scheduler.add_job(expire_pending_tickets, 'cron', minute=45)
scheduler.add_job(send_monthly_event_invoice, 'cron', day=1, month='1-12')
scheduler.add_job(event_invoices_mark_due, 'cron', hour=5)
scheduler.start()


@app.errorhandler(500)
def internal_server_error(error):
    if current_app.config['PROPOGATE_ERROR'] is True:
        exc = JsonApiException({'pointer': ''}, str(error))
    else:
        exc = JsonApiException({'pointer': ''}, 'Unknown error')
    return make_response(json.dumps(jsonapi_errors([exc.to_dict()])), exc.status,
                         {'Content-Type': 'application/vnd.api+json'})


if __name__ == '__main__':
    current_app.run()

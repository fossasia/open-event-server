# Ignore ExtDeprecationWarnings for Flask 0.11 - see http://stackoverflow.com/a/38080580
import warnings

from flask.exthook import ExtDeprecationWarning

warnings.simplefilter('ignore', ExtDeprecationWarning)
# Keep it before flask extensions are imported

import re

from pytz import timezone
import base64
from StringIO import StringIO

import qrcode
from forex_python.converter import CurrencyCodes
from pytz import utc

from app.helpers.scheduled_jobs import send_mail_to_expired_orders, empty_trash, send_after_event_mail, \
    send_event_fee_notification, send_event_fee_notification_followup

import arrow
from celery import Celery
from celery.signals import after_task_publish
from flask.ext.htmlmin import HTMLMIN
import logging
import os.path
from os import environ
import sys
import json
from flask import Flask, session
from app.settings import get_settings, get_setts
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import current_user
from flask import render_template
from flask import request
from flask.ext.jwt import JWT
from datetime import timedelta, datetime
import humanize

import sqlalchemy as sa

from nameparser import HumanName
import stripe
from app.settings import get_settings
from app.helpers.flask_helpers import SilentUndefined, camel_case, slugify, MiniJSONEncoder
from app.helpers.payment import forex
from app.models import db
from app.models.user import User
from app.models.event import Event
from app.models.session import Session
from helpers.jwt import jwt_authenticate, jwt_identity
from helpers.formatter import operation_name
from app.helpers.data_getter import DataGetter
from app.api.helpers.errors import NotFoundError, PermissionDeniedError, ServerError, ValidationError
from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers.data import DataManager, delete_from_db
from app.helpers.helpers import send_after_event
from app.helpers.cache import cache
from app.helpers.babel import babel
from helpers.helpers import send_email_for_expired_orders
from werkzeug.contrib.profiler import ProfilerMiddleware

from flask.ext.sqlalchemy import get_debug_queries
from config import ProductionConfig, LANGUAGES
from app.helpers.auth import AuthManager
from app.views import BlueprintsManager

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


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


def create_app():
    babel.init_app(app)
    BlueprintsManager.register(app)
    Migrate(app, db)

    app.config.from_object(environ.get('APP_CONFIG', 'config.ProductionConfig'))
    db.init_app(app)
    _manager = Manager(app)
    _manager.add_command('db', MigrateCommand)

    if app.config['CACHING']:
        cache.init_app(app, config={'CACHE_TYPE': 'simple'})
    else:
        cache.init_app(app, config={'CACHE_TYPE': 'null'})

    stripe.api_key = 'SomeStripeKey'
    app.secret_key = 'super secret key'
    app.json_encoder = MiniJSONEncoder
    app.config['BABEL_DEFAULT_LOCALE'] = 'en'
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.undefined = SilentUndefined
    app.jinja_env.filters['operation_name'] = operation_name

    # set up jwt
    app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24 * 60 * 60)
    app.config['JWT_AUTH_URL_RULE'] = None
    _jwt = JWT(app, jwt_authenticate, jwt_identity)

    # setup celery
    app.config['CELERY_BROKER_URL'] = environ.get('REDIS_URL', 'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']

    HTMLMIN(app)
    AuthManager.init_login(app)

    if app.config['TESTING'] and app.config['PROFILE']:
        # Profiling
        app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

    # API version 2
    with app.app_context():
        from app.api import api_v1
        app.register_blueprint(api_v1)

    sa.orm.configure_mappers()

    return app, _manager, db, _jwt


current_app, manager, database, jwt = create_app()


@app.errorhandler(404)
def page_not_found(e):
    if request_wants_json():
        error = NotFoundError()
        return json.dumps(error.to_dict()), getattr(error, 'code', 404)
    return render_template('gentelella/errors/404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    if request_wants_json():
        error = PermissionDeniedError()
        return json.dumps(error.to_dict()), getattr(error, 'code', 403)
    return render_template('gentelella/errors/403.html'), 403


@app.errorhandler(500)
def server_error(e):
    if request_wants_json():
        error = ServerError()
        return json.dumps(error.to_dict()), getattr(error, 'code', 500)
    return render_template('gentelella/errors/500.html'), 500


@app.errorhandler(400)
def bad_request(e):
    if request_wants_json():
        error = ValidationError(field='unknown')
        return json.dumps(error.to_dict()), getattr(error, 'code', 400)
    return render_template('gentelella/errors/400.html'), 400


# taken from http://flask.pocoo.org/snippets/45/
def request_wants_json():
    best = request.accept_mimetypes.best_match(
        ['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


@app.context_processor
def all_languages():
    return dict(all_languages=LANGUAGES)


@app.context_processor
def selected_lang():
    return dict(selected_lang=get_locale())


@app.context_processor
def locations():
    def get_locations_of_events():
        return DataGetter.get_locations_of_events()

    return dict(locations=get_locations_of_events)


@app.context_processor
def get_key_settings():
    key_settings = get_settings()
    return dict(key_settings=key_settings)


@app.context_processor
def get_app_name():
    return dict(app_name=get_settings()['app_name'])


@app.context_processor
def fee_helpers():
    def get_fee(currency):
        from app.helpers.payment import get_fee
        return get_fee(currency)

    return dict(get_fee=get_fee)


@app.context_processor
def qrcode_generator():
    def generate_qr(text):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image()

        buffer = StringIO()
        img.save(buffer, format="JPEG")
        img_str = base64.b64encode(buffer.getvalue())
        return img_str

    return dict(generate_qr=generate_qr)


@app.context_processor
def event_types():
    event_types = DataGetter.get_event_types()
    return dict(event_typo=event_types[:10])


@app.context_processor
def base_dir():
    return dict(base_dir=app.config['BASE_DIR'])


@app.context_processor
def pages():
    pages = DataGetter.get_all_pages(get_locale())
    return dict(system_pages=pages)


@app.context_processor
def datetime_now():
    return dict(datetime_now=datetime.now())


@app.context_processor
def social_settings():
    settings = get_setts()
    return dict(settes=settings)


@app.context_processor
def app_logo():
    logo = DataGetter.get_custom_placeholder_by_name('Logo')
    return dict(logo=logo)


@app.context_processor
def app_avatar():
    avatar = DataGetter.get_custom_placeholder_by_name('Avatar')
    return dict(avatar=avatar)


@app.template_filter('pretty_name')
def pretty_name_filter(string):
    string = str(string)
    string = string.replace('_', ' ')
    string = string.title()
    return string


@app.template_filter('currency_symbol')
def currency_symbol_filter(currency_code):
    symbol = CurrencyCodes().get_symbol(currency_code)
    return symbol if symbol else '$'


@app.template_filter('currency_name')
def currency_name_filter(currency_code):
    name = CurrencyCodes().get_currency_name(currency_code)
    return name if name else ''


@app.template_filter('camel_case')
def camel_case_filter(string):
    return camel_case(string)


@app.template_filter('slugify')
def slugify_filter(string):
    return slugify(string)


@app.template_filter('humanize')
def humanize_filter(time):
    if not time:
        return "N/A"
    return arrow.get(time).humanize()


@app.template_filter('humanize_alt')
def humanize_alt_filter(time):
    if not time:
        return "N/A"
    return humanize.naturaltime(datetime.now() - time)


@app.template_filter('time_format')
def time_filter(time):
    if not time:
        return "N/A"
    return time


@app.template_filter('firstname')
def firstname_filter(string):
    if string:
        return HumanName(string).first
    else:
        return 'N/A'


@app.template_filter('middlename')
def middlename_filter(string):
    if string:
        return HumanName(string).middle
    else:
        return 'N/A'


@app.template_filter('lastname')
def lastname_filter(string):
    if string:
        return HumanName(string).last
    else:
        return 'N/A'


@app.template_filter('money')
def money_filter(string):
    return '{:20,.2f}'.format(float(string))


@app.template_filter('datetime')
def simple_datetime_display(date):
    return date.strftime('%B %d, %Y %I:%M %p')


@app.template_filter('external_url')
def external_url(url):
    """Returns an external URL for the given `url`.
    If URL is already external, it remains unchanged.
    """
    url_pattern = r'^(https?)://.*$'
    scheme = re.match(url_pattern, url)
    if not scheme:
        url_root = request.url_root.rstrip('/')
        return '{}{}'.format(url_root, url)
    else:
        return url


@app.template_filter('localize_dt')
def localize_dt(dt, tzname):
    """Accepts a Datetime object and a Timezone name.
    Returns Timezone aware Datetime.
    """
    localized_dt = timezone(tzname).localize(dt)
    return localized_dt.isoformat()


@app.template_filter('localize_dt_obj')
def localize_dt_obj(dt, tzname):
    """Accepts a Datetime object and a Timezone name.
    Returns Timezone aware Datetime Object.
    """
    localized_dt = timezone(tzname).localize(dt)
    return localized_dt


@app.template_filter('as_timezone')
def as_timezone(dt, tzname):
    """Accepts a Time aware Datetime object and a Timezone name.
        Returns Converted Timezone aware Datetime Object.
        """
    converted_dt = dt.astimezone(timezone(tzname))
    return converted_dt


@app.context_processor
def fb_app_id():
    fb_app_id = get_settings()['fb_client_id']
    return dict(fb_app_id=fb_app_id)


@app.context_processor
def flask_helpers():
    def string_empty(string):
        from app.helpers.helpers import string_empty
        return string_empty(string)

    def current_date(format='%a, %B %d %I:%M %p', **kwargs):
        return (datetime.now() + timedelta(**kwargs)).strftime(format)

    return dict(string_empty=string_empty, current_date=current_date, forex=forex)


@app.context_processor
def versioning_manager():
    def count_versions(model_object):
        from sqlalchemy_continuum.utils import count_versions
        return count_versions(model_object)

    def changeset(model_object):
        from sqlalchemy_continuum import changeset
        return changeset(model_object)

    def transaction_class(version_object):
        from sqlalchemy_continuum import transaction_class
        transaction = transaction_class(version_object)
        return transaction.query.get(version_object.transaction_id)

    def version_class(model_object):
        from sqlalchemy_continuum import version_class
        return version_class(model_object)

    def get_user_name(transaction_object):
        if transaction_object and transaction_object.user_id:
            user = DataGetter.get_user(transaction_object.user_id)
            return user.email
        return 'unconfigured@example.com'

    def side_by_side_diff(changeset_entry):
        from app.helpers.versioning import side_by_side_diff
        for side_by_side_diff_entry in side_by_side_diff(changeset_entry[0],
                                                         changeset_entry[1]):
            yield side_by_side_diff_entry

    return dict(count_versions=count_versions,
                changeset=changeset,
                transaction_class=transaction_class,
                version_class=version_class,
                side_by_side_diff=side_by_side_diff,
                get_user_name=get_user_name)


# http://stackoverflow.com/questions/26724623/
@app.before_request
def track_user():
    if current_user.is_authenticated:
        current_user.update_lat()


def make_celery(app):
    celery = Celery(app.import_name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)
    task_base = celery.Task

    class ContextTask(task_base):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return task_base.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(current_app)


# http://stackoverflow.com/questions/9824172/find-out-whether-celery-task-exists
@after_task_publish.connect
def update_sent_state(sender=None, body=None, **kwargs):
    # the task may not exist if sent using `send_task` which
    # sends tasks by name, so fall back to the default result backend
    # if that is the case.
    task = celery.tasks.get(sender)
    backend = task.backend if task else celery.backend
    backend.store_result(body['id'], None, 'WAITING')


# register celery tasks. removing them will cause the tasks to not function. so don't remove them
# it is important to register them after celery is defined to resolve circular imports
import api.helpers.tasks
import helpers.tasks


@app.context_processor
def integrate_socketio():
    integrate = current_app.config.get('INTEGRATE_SOCKETIO', False)
    return dict(integrate_socketio=integrate)


scheduler = BackgroundScheduler(timezone=utc)
scheduler.add_job(send_mail_to_expired_orders, 'interval', hours=5)
scheduler.add_job(empty_trash, 'cron', day_of_week='mon-fri', hour=5, minute=30)
scheduler.add_job(send_after_event_mail, 'cron', day_of_week='mon-fri', hour=5, minute=30)
scheduler.add_job(send_event_fee_notification, 'cron', day=1)
scheduler.add_job(send_event_fee_notification_followup, 'cron', day=15)
scheduler.start()


# Testing database performance
@app.after_request
def after_request(response):
    for query in get_debug_queries():
        if query.duration >= ProductionConfig.DATABASE_QUERY_TIMEOUT:
            app.logger.warning("SLOW QUERY: %s\nParameters: %s\nDuration: %fs\nContext: %s\n" % (query.statement,
                                                                                                 query.parameters,
                                                                                                 query.duration,
                                                                                                 query.context))
    return response


# Flask-SocketIO integration
socketio = None
if current_app.config.get('INTEGRATE_SOCKETIO', False):
    from eventlet import monkey_patch
    from flask_socketio import SocketIO, emit, join_room

    monkey_patch()

    async_mode = 'eventlet'
    socketio = SocketIO(current_app, async_mode=async_mode)


    @socketio.on('connect', namespace='/notifs')
    def connect_handler_notifs():
        if current_user.is_authenticated():
            user_room = 'user_{}'.format(session['user_id'])
            join_room(user_room)
            emit('notifs-response', {'meta': 'WS connected'}, namespace='/notifs')


    @socketio.on('connect', namespace='/notifpage')
    def connect_handler_notif_page():
        if current_user.is_authenticated():
            user_room = 'user_{}'.format(session['user_id'])
            join_room(user_room)
            emit('notifpage-response', {'meta': 'WS notifpage connected'}, namespace='/notifpage')

if __name__ == '__main__':
    if current_app.config.get('INTEGRATE_SOCKETIO', False):
        socketio.run(current_app)
    else:
        current_app.run()


@babel.localeselector
def get_locale():
    try:
        return request.cookies["selected_lang"]
    except:
        return request.accept_languages.best_match(LANGUAGES.keys())

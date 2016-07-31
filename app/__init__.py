"""Copyright 2015 Rafal Kowalski"""

# Ignore ExtDeprecationWarnings for Flask 0.11 - see http://stackoverflow.com/a/38080580
import warnings

from flask.exthook import ExtDeprecationWarning
from pytz import utc

warnings.simplefilter('ignore', ExtDeprecationWarning)
# Keep it before flask extensions are imported
import arrow
from celery import Celery
from flask.ext.htmlmin import HTMLMIN
import logging
import os.path
from os import environ
import sys
import json
from flask import Flask, session
from flask.ext.autodoc import Autodoc
from app.settings import get_settings
from flask.ext.cors import CORS
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
from app.helpers.flask_helpers import SilentUndefined, camel_case, slugify, MiniJSONEncoder
from app.models import db
from app.models.user import User
from app.models.event import Event
from app.models.session import Session
from app.views.admin.admin import AdminView
from helpers.jwt import jwt_authenticate, jwt_identity
from helpers.formatter import operation_name
from app.helpers.data_getter import DataGetter
from app.views.api_v1_views import app as api_v1_routes
from app.views.sitemap import app as sitemap_routes
from app.api.helpers.errors import NotFoundError
from apscheduler.schedulers.background import BackgroundScheduler
from app.helpers.data import DataManager, delete_from_db
from app.helpers.helpers import send_after_event
from app.helpers.cache import cache
from sqlalchemy_continuum import transaction_class

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def create_app():
    Autodoc(app)
    # cal = Calendar()

    app.register_blueprint(api_v1_routes)
    app.register_blueprint(sitemap_routes)
    Migrate(app, db)

    app.config.from_object(environ.get('APP_CONFIG',
                                       'config.ProductionConfig'))
    db.init_app(app)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    cache.init_app(app)

    CORS(app)
    stripe.api_key = 'SomeStripeKey'
    app.secret_key = 'super secret key'
    app.json_encoder = MiniJSONEncoder
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
    app.config['STATIC_URL'] = '/static/'
    app.config['STATIC_ROOT'] = 'staticfiles'
    app.config['STATICFILES_DIRS'] = (os.path.join(BASE_DIR, 'static'), )
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    # app.config['SERVER_NAME'] = 'open-event-dev.herokuapp.com'
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.undefined = SilentUndefined
    app.jinja_env.filters['operation_name'] = operation_name
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # set up jwt
    app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24 * 60 * 60)
    app.config['JWT_AUTH_URL_RULE'] = None
    jwt = JWT(app, jwt_authenticate, jwt_identity)

    # setup celery
    app.config['CELERY_BROKER_URL'] = environ.get('REDIS_URL',
                                                  'redis://localhost:6379/0')
    app.config['CELERY_RESULT_BACKEND'] = app.config['CELERY_BROKER_URL']

    HTMLMIN(app)
    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    # API version 2
    with app.app_context():
        from app.api import api_v2
        app.register_blueprint(api_v2)

    sa.orm.configure_mappers()

    return app, manager, db, jwt

current_app, manager, database, jwt = create_app()

@app.errorhandler(404)
def page_not_found(e):
    if request_wants_json():
        error = NotFoundError()
        return json.dumps(error.to_dict()), getattr(error, 'code', 404)
    return render_template('404.html'), 404


@app.errorhandler(403)
def forbidden(e):
    if request_wants_json():
        return json.dumps({"error": "forbidden"}), 403
    return render_template('gentelella/admin/forbidden.html'), 403


# taken from http://flask.pocoo.org/snippets/45/
def request_wants_json():
    best = request.accept_mimetypes.best_match(
        ['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']

@app.context_processor
def locations():
    def get_locations_of_events():
        return DataGetter.get_locations_of_events()
    return dict(locations=get_locations_of_events)


@app.context_processor
def event_types():
    event_types = DataGetter.get_event_types()
    return dict(event_typo=event_types[:10])


@app.context_processor
def pages():
    pages = DataGetter.get_all_pages()
    return dict(system_pages=pages)


@app.context_processor
def social_settings():
    settings = get_settings()
    return dict(settings=settings)


@app.template_filter('pretty_name')
def pretty_name_filter(s):
    s = str(s)
    s = s.replace('_', ' ')
    s = s.title()
    return s


@app.template_filter('camel_case')
def camel_case_filter(s):
    return camel_case(s)


@app.template_filter('slugify')
def slugify_filter(s):
    return slugify(s)


@app.template_filter('humanize')
def humanize_filter(time):
    if time is None:
        return "N/A"
    return arrow.get(time).humanize()


@app.template_filter('humanize_alt')
def humanize_filter(time):
    if time is None:
        return "N/A"
    return humanize.naturaltime(datetime.now() - time)

@app.template_filter('firstname')
def firstname_filter(string):
    return HumanName(string).first

@app.template_filter('middlename')
def middlename_filter(string):
    return HumanName(string).middle

@app.template_filter('lastname')
def lastname_filter(string):
    return HumanName(string).last

@app.context_processor
def flask_helpers():
    def string_empty(string):
        from app.helpers.helpers import string_empty
        return string_empty(string)

    def current_date(format='%a, %B %d %I:%M %p', **kwargs):
        return (datetime.now() + timedelta(**kwargs)).strftime(format)

    return dict(string_empty=string_empty, current_date=current_date)


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
    TaskBase = celery.Task

    class ContextTask(TaskBase):
        abstract = True

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return TaskBase.__call__(self, *args, **kwargs)

    celery.Task = ContextTask
    return celery


celery = make_celery(current_app)
import api.helpers.tasks


@app.before_first_request
def set_secret():
    current_app.secret_key = get_settings()['secret']

@app.before_first_request
def set_stripe_key():
    stripe.api_key = get_settings()['stripe_secret_key']

def send_after_event_mail():
    with app.app_context():
        events = Event.query.all()
        for event in events:
            upcoming_events = DataGetter.get_upcoming_events(event.id)
            organizers = DataGetter.get_user_event_roles_by_role_name(
                event.id, 'organizer')
            speakers = DataGetter.get_user_event_roles_by_role_name(event.id,
                                                                    'speaker')
            if datetime.now() > event.end_time:
                for speaker in speakers:
                    send_after_event(speaker.user.email, event.id,
                                     upcoming_events)
                for organizer in organizers:
                    send_after_event(organizer.user.email, event.id,
                                     upcoming_events)

#logging.basicConfig()
sched = BackgroundScheduler(timezone=utc)
sched.add_job(send_after_event_mail,
              'cron',
              day_of_week='mon-fri',
              hour=5,
              minute=30)

#sched.start()


def empty_trash():
    with app.app_context():
        print 'HELLO'
        events = Event.query.filter_by(in_trash=True)
        users = User.query.filter_by(in_trash=True)
        sessions = Session.query.filter_by(in_trash=True)
        for event in events:
            if datetime.now() - event.trash_date >= timedelta(days=30):
                DataManager.delete_event(event.id)

        for user in users:
            if datetime.now() - user.trash_date >= timedelta(days=30):
                transaction = transaction_class(Event)
                transaction.query.filter_by(user_id=user.id).delete()
                delete_from_db(user, "User deleted permanently")

        for session_ in sessions:
            if datetime.now() - session_.trash_date >= timedelta(days=30):
                delete_from_db(session_, "Session deleted permanently")


trash_sched = BackgroundScheduler(timezone=utc)
trash_sched.add_job(
    empty_trash, 'cron',
    day_of_week='mon-fri',
    hour=5, minute=30)
trash_sched.start()

# Flask-SocketIO integration

if current_app.config.get('PRODUCTION', False):
    from eventlet import monkey_patch
    from flask_socketio import SocketIO, emit, join_room

    monkey_patch()

    async_mode = 'eventlet'
    socketio = SocketIO(current_app, async_mode=async_mode)

    @socketio.on('connect', namespace='/notifs')
    def connect_handler():
        if current_user.is_authenticated():
            user_room = 'user_{}'.format(session['user_id'])
            join_room(user_room)
            emit('response', {'meta': 'WS connected'})


if __name__ == '__main__':
    if current_app.config.get('PRODUCTION', False):
        socketio.run(current_app)
    else:
        current_app.run()

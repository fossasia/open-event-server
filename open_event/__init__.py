"""Copyright 2015 Rafal Kowalski"""
import arrow
from dateutil import tz
from flask.ext.htmlmin import HTMLMIN
import logging
import os.path
from os import environ
import sys
import json
from collections import Counter
from flask import Flask
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.login import current_user
from flask import render_template
from flask import request
from flask.ext.jwt import JWT
from datetime import timedelta, time

from icalendar import Calendar, Event
import humanize
import sqlalchemy as sa
from markupsafe import Markup

from open_event.helpers.flask_helpers import SilentUndefined
from open_event.helpers.helpers import string_empty
from open_event.models import db
from open_event.views.admin.admin import AdminView
from helpers.jwt import jwt_authenticate, jwt_identity
from helpers.formatter import operation_name
from open_event.helpers.data_getter import DataGetter
from open_event.views.api_v1_views import app as api_v1_routes
import requests


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)

def create_app():
    auto = Autodoc(app)
    cal = Calendar()
    event = Event()

    app.register_blueprint(api_v1_routes)
    migrate = Migrate(app, db)

    app.config.from_object(environ.get('APP_CONFIG', 'config.ProductionConfig'))
    db.init_app(app)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    cors = CORS(app)
    app.secret_key = 'super secret key'
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
    app.config['STATIC_URL'] = '/static/'
    app.config['STATIC_ROOT'] = 'staticfiles'
    app.config['STATICFILES_DIRS'] = (os.path.join(BASE_DIR, 'static'),)
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
    app.jinja_env.add_extension('jinja2.ext.do')
    app.jinja_env.add_extension('jinja2.ext.loopcontrols')
    app.jinja_env.undefined = SilentUndefined
    app.jinja_env.filters['operation_name'] = operation_name
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # set up jwt
    app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24*60*60)
    app.config['JWT_AUTH_URL_RULE'] = None
    jwt = JWT(app, jwt_authenticate, jwt_identity)

    HTMLMIN(app)
    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    # API version 2
    with app.app_context():
        from open_event.api import api_v2
        app.register_blueprint(api_v2)

    sa.orm.configure_mappers()

    return app, manager, db, jwt


@app.errorhandler(404)
def page_not_found(e):
    if request_wants_json():
        return json.dumps({"error": "not_found"}), 404
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
    names = []
    for event in DataGetter.get_all_live_events():
        if not string_empty(event.location_name) and not string_empty(event.latitude) and not string_empty(event.longitude):
            response = requests.get("https://maps.googleapis.com/maps/api/geocode/json?latlng=" + str(event.latitude) + "," + str(
                event.longitude)).json()
            if response['status'] == u'OK':
                for addr in response['results'][0]['address_components']:
                    if addr['types'] == ['locality', 'political']:
                        names.append(addr['short_name'])

    cnt = Counter()
    for location in names:
        cnt[location] += 1
    return dict(locations=[v for v, k in cnt.most_common()][:10])

@app.context_processor
def event_types():
    event_types = DataGetter.get_event_types()
    return dict(event_typo=event_types[:10])

@app.template_filter('pretty_name')
def pretty_name_filter(s):
    s = str(s)
    s = s.replace('_', ' ')
    s = s.title()
    return s

@app.template_filter('humanize')
def humanize_filter(time):
    return arrow.get(time).humanize()

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
        user = DataGetter.get_user(transaction_object.user_id)
        return user.email

    def side_by_side_diff(changeset_entry):
        from open_event.helpers.versioning import side_by_side_diff
        for side_by_side_diff_entry in side_by_side_diff(changeset_entry[0], changeset_entry[1]):
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


current_app, manager, database, jwt = create_app()


if __name__ == '__main__':
    current_app.run()

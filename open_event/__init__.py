"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
from os import environ
import sys
import json

from flask import Flask
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask import render_template
from flask import request
from flask.ext.jwt import JWT
from datetime import timedelta

from icalendar import Calendar, Event

from open_event.models import db
from open_event.views.admin.admin import AdminView
from helpers.jwt import jwt_authenticate, jwt_identity
from open_event.views.views import app as routes

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


def create_app():
    auto = Autodoc(app)
    cal = Calendar()
    event = Event()

    app.register_blueprint(routes)
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
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # set up jwt
    app.config['JWT_AUTH_USERNAME_KEY'] = 'email'
    app.config['JWT_EXPIRATION_DELTA'] = timedelta(seconds=24*60*60)
    app.config['JWT_AUTH_URL_RULE'] = None
    jwt = JWT(app, jwt_authenticate, jwt_identity)

    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    # API version 2
    with app.app_context():
        from open_event.api import api_v2
        app.register_blueprint(api_v2)

    return app, manager, db, jwt


@app.errorhandler(404)
def page_not_found(e):
    if request_wants_json():
        return json.dumps({"error": "endpoint_not_found"})
    return render_template('404.html'), 404


# taken from http://flask.pocoo.org/snippets/45/
def request_wants_json():
    best = request.accept_mimetypes.best_match(
        ['application/json', 'text/html'])
    return best == 'application/json' and \
        request.accept_mimetypes[best] > \
        request.accept_mimetypes['text/html']


current_app, manager, database, jwt = create_app()


if __name__ == '__main__':
    current_app.run()

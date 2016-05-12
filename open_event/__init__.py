"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import sys
import json

from flask import Flask
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask import render_template
from flask import request

from icalendar import Calendar, Event
from flask_debugtoolbar import DebugToolbarExtension

import open_event.models.event_listeners
from open_event.models import db
from open_event.views.admin.admin import AdminView

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__)


def create_app():
    auto = Autodoc(app)
    cal = Calendar()
    event = Event()

    from open_event.views.views import app as routes
    app.register_blueprint(routes)
    migrate = Migrate(app, db)

    db.init_app(app)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    cors = CORS(app)
    app.secret_key = 'super secret key'
    app.config.from_object('config.ProductionConfig')
    # app.config.from_object('config.LocalSQLITEConfig')
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
    app.config['STATIC_URL'] = '/static/'
    app.config['STATIC_ROOT'] = 'staticfiles'
    app.config['STATICFILES_DIRS'] = (os.path.join(BASE_DIR, 'static'),)
    app.config['SQLALCHEMY_RECORD_QUERIES'] = True
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    # Flask-DebugToolbar Configuration
    # Set DEBUG_TB_ENABLED as False in Production
    app.config['DEBUG_TB_ENABLED'] = True
    app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
    DebugToolbarExtension(app)

    return app, manager, db


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

current_app, manager, database = create_app()

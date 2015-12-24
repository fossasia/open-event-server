"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import sys

from flask import Flask
from flask.ext.cors import CORS
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager

import open_event.models.event_listeners
from open_event.models import db
from open_event.views.admin.admin import AdminView
from flask.ext.autodoc import Autodoc

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)
    auto=Autodoc(app)
    from open_event.views.views import app as routes
    app.register_blueprint(routes)
    migrate = Migrate(app, db)

    db.init_app(app)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    cors = CORS(app)
    app.secret_key = 'super secret key'
    app.config.from_object('config.ProductionConfig')
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'
    app.config['STATIC_URL'] = '/static/'
    app.config['STATIC_ROOT'] = 'staticfiles'
    app.config['STATICFILES_DIRS'] = (os.path.join(BASE_DIR, 'static'),)
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    return app, manager, db


current_app, manager, database = create_app()

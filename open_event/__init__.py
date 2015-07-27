"""Copyright 2015 Rafal Kowalski"""
import sys
import logging

from flask import Flask
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.cors import CORS

import open_event.models.event_listeners
from open_event.models import db
from open_event.views.admin.admin import AdminView
import os.path

def create_app():
    app = Flask(__name__)
    from open_event.views.views import app as routes
    app.register_blueprint(routes)
    migrate = Migrate(app, db)

    db.init_app(app)
    manager = Manager(app)
    manager.add_command('db', MigrateCommand)

    cors = CORS(app)
    app.secret_key = 'super secret key'
    app.config.from_object('config.LocalPSQLConfig')
    app.config['UPLOADS_FOLDER'] = os.path.realpath('.') + '/static/'
    app.config['FILE_SYSTEM_STORAGE_FILE_VIEW'] = 'static'

    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)

    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    return app, manager, db


current_app, manager, database = create_app()

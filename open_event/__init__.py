"""Copyright 2015 Rafal Kowalski"""
import logging
import os.path
import sys

from flask import Flask
from flask.ext.autodoc import Autodoc
from flask.ext.cors import CORS
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from flask.ext.assets import Environment, Bundle
from icalendar import Calendar, Event

import open_event.models.event_listeners
from open_event.models import db
from open_event.views.admin.admin import AdminView

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def create_app():
    app = Flask(__name__)

    # jinja config for trimming unnecessary line break and whitespaces
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True

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
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.INFO)
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)

    # Assets minification using Flask-Assets plugin
    assets = Environment(app)
    # Defining asset bundles
    common_css = Bundle('css/vendor/bootstrap.min.css',
                        'css/roboto.css',
                        'css/material/material-custom.css',
                        'css/material/ripples.css',
                        'css/open-event.css',
                        filters='cssrewrite,datauri,cssmin', output='gen/common.styles.css')

    common_js = Bundle('js/vendor/jquery-2.1.1.min.js',
                       'js/vendor/bootstrap.min.js',
                       'js/vendor/moment-2.8.4.min.js',
                       'js/vendor/select2.min.js',
                       'js/material.js',
                       filters='jsmin', output='gen/common.scripts.js')

    form_css = Bundle('css/vendor/select2/select2.css',
                      'css/vendor/select2/select2-bootstrap3.css',
                      'css/vendor/daterangepicker-bs3.css',
                      filters='cssrewrite,datauri,cssmin', output='gen/form.styles.css')

    form_js = Bundle('js/vendor/daterangepicker.js',
                     'js/vendor/form-1.0.0.js',
                     filters='jsmin', output='gen/form.scripts.js')

    list_css = Bundle('css/vendor/dataTables.bootstrap.css',
                      filters='cssrewrite,datauri,cssmin', output='gen/list.styles.css')

    list_js = Bundle('js/vendor/datatables/jquery.dataTables.min.js',
                     'js/vendor/datatables/dataTables.bootstrap.js',
                     filters='jsmin', output='gen/list.scripts.js')

    # Registering bundles
    assets.register('common_css', common_css)
    assets.register('common_js', common_js)

    assets.register('form_css', form_css)
    assets.register('form_js', form_js)

    assets.register('list_css', list_css)
    assets.register('list_js', list_js)

    admin_view = AdminView("Open Event")
    admin_view.init(app)
    admin_view.init_login(app)

    return app, manager, db


current_app, manager, database = create_app()

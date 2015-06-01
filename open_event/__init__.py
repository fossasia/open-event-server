"""Written by - Rafal Kowalski"""
import sys
import logging

from flask import Flask, render_template, jsonify, url_for
from flask.ext.migrate import Migrate, MigrateCommand
from flask.ext.script import Manager
from open_event.models import db
from open_event.views.admin.admin import AdminView
from flask.ext.cors import CORS

app = Flask(__name__)
from views import views
migrate = Migrate(app, db)
cors = CORS(app)
app.secret_key = 'super secret key'
app.config.from_object('config')

manager = Manager(app)
manager.add_command('db', MigrateCommand)

app.logger.addHandler(logging.StreamHandler(sys.stdout))
app.logger.setLevel(logging.ERROR)

AdminView(app, "Open Event").init()
db.init_app(app)

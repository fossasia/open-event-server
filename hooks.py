import dredd_hooks as hooks
import requests
from flask_migrate import Migrate, stamp

from flask import Flask
from app.models import db
from populate_db import populate
from app.helpers.data import DataManager

stash = {}
api_username = "open_event_test_user@fossasia.org"
api_password = "fossasia"
api_uri = "http://localhost:5000/auth/session"


@hooks.before_all
def before_all(transaction):
    app = Flask(__name__)
    app.config.from_object('config.TestingConfig')
    db.init_app(app)
    Migrate(app, db)
    stash['app'] = app
    stash['db'] = db


def obtain_token():
    data = {
        "email": api_username,
        "password": api_password
    }
    url = api_uri
    response = requests.post(url, json=data)
    response.raise_for_status()
    parsed_body = response.json()
    token = parsed_body["access_token"]
    return token


@hooks.before_each
def before_each(transaction):
    with stash['app'].app_context():
        db.create_all()
        stamp()
        DataManager.create_super_admin(api_username, api_password)
        populate_without_print()

    if 'token' in stash:
        print('adding a token')
    else:
        stash['token'] = obtain_token()

    transaction['request']['headers']['Authorization'] = "JWT " + stash['token']


@hooks.after_each
def after_each(transaction):
    with stash['app'].app_context():
        db.session.remove()
        db.engine.execute("drop schema if exists public cascade")
        db.engine.execute("create schema public")

import logging
import sys

from flask import current_app
from app.instance import create_app as main_create_app
from app.models import db
from app.models.setting import Environment
from app.settings import set_settings


def create_app():
    app = main_create_app()
    app.config.from_object('config.TestingConfig')
    app.logger.addHandler(logging.StreamHandler(sys.stdout))
    app.logger.setLevel(logging.ERROR)
    return app


class Setup:
    @staticmethod
    def create_app():
        test_app = create_app()
        with test_app.test_request_context():
            db.engine.execute('create extension if not exists citext')
            db.create_all()
            set_settings(app_name='Open Event', app_environment=Environment.TESTING)

        return test_app

    @staticmethod
    def drop_db():
        with current_app.test_request_context():
            db.session.remove()
            if current_app.config['SQLALCHEMY_DATABASE_URI'].find('postgresql://') > -1:
                # drop_all has problems with foreign keys in postgres database
                # (cyclic dependency)
                db.engine.execute("drop schema if exists public cascade")
                db.engine.execute("create schema public")
            else:
                # drop all works for SQLite and should work for other DBMS
                # like MySQL, Mongo etc
                db.drop_all()

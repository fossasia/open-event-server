"""Copyright 2015 Rafal Kowalski"""
import os

from open_event import current_app as app
from open_event.models import db

_basedir = os.path.abspath(os.path.dirname(__file__))


class Setup(object):
    @staticmethod
    def create_app():
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(_basedir, 'test.db')
        app.secret_key = 'super secret key'
        with app.test_request_context():
            db.create_all()
        return app.test_client()

    @staticmethod
    def drop_db():
        with app.test_request_context():
            db.session.remove()
            db.drop_all()

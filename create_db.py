import re
import sys
import getpass
import eventlet

from app import current_app
from flask.ext.migrate import stamp
from app.helpers.data import DataManager
from app.models import db
from populate_db import populate


def _validate_email(email):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        print '\nInvalid email address'
        sys.exit(1)


def _validate_password(password):
    if len(password) < 4:
        print '\nPassword should have minimum 4 characters'
        sys.exit(1)


def create_default_user():
    print "Your login is 'super_admin'."
    email = raw_input("Enter email for super_admin    : ")
    _validate_email(email)
    getpass.os = eventlet.patcher.original('os')
    password = getpass.getpass("Enter password for super_admin : ")
    _validate_password(password)
    DataManager.create_super_admin(email, password)


if __name__ == "__main__":
    with current_app.app_context():
        db.create_all()
        stamp()
        create_default_user()
        populate()

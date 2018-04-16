from __future__ import print_function

import getpass
import re
import sys

from builtins import input
from flask_migrate import stamp

from app import current_app
from app.models import db
from populate_db import populate
from tests.unittests.auth_helper import create_super_admin


def _validate_email(email):
    if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
        print('\nInvalid email address')
        sys.exit(1)


def _validate_password(password):
    if len(password) < 4:
        print('\nPassword should have minimum 4 characters')
        sys.exit(1)


def create_default_user():
    print("Your login is 'super_admin'.")
    email = input("Enter email for super_admin    : ")
    _validate_email(email)
    password = getpass.getpass("Enter password for super_admin : ")
    _validate_password(password)
    create_super_admin(email, password)


if __name__ == "__main__":
    with current_app.app_context():
        db.create_all()
        stamp()
        create_default_user()
        populate()

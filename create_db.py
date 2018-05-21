import argparse
import getpass
import re
import sys

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


def create_default_user(email, password):
    print("Your login is 'super_admin'.")
    if not email:
        email = input("Enter email for super_admin    : ")
    _validate_email(email)
    if not password:
        password = getpass.getpass("Enter password for super_admin : ")
    _validate_password(password)
    create_super_admin(email, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs='?', help="The email for super_admin.", default='')
    parser.add_argument("password", nargs='?', help="The password for super_admin.", default='')
    parser.parse_args()
    email = parser.email if hasattr(parser, "email") else ''
    password = parser.password if hasattr(parser, "password") else ''
    with current_app.app_context():
        db.create_all()
        stamp()
        create_default_user(email, password)
        populate()

import argparse
import getpass
import re

from flask_migrate import stamp

from app.instance import current_app
from app.models import db
from populate_db import populate
from tests.all.integration.auth_helper import create_super_admin


def create_default_user(email, password):
    print("Your login is 'super_admin'.")
    if not email:
        ask_email = True
        while ask_email:
            email = input("Enter email for super_admin: ")
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                print('\nInvalid email address\n')
                continue
            ask_email = False
    if not password:
        ask_password = True
        while ask_password:
            password = getpass.getpass("Enter password for super_admin: ")
            if len(password) < 8:
                print('\nPassword should have minimum 8 characters')
                continue
            repassword = getpass.getpass("Enter your password again to confirm: ")
            if password != repassword:
                print('\nPassword did not match')
                continue
            ask_password = False
    create_super_admin(email, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs='?', help="The email for super_admin.", default='')
    parser.add_argument(
        "password", nargs='?', help="The password for super_admin.", default=''
    )
    parsed = parser.parse_args()
    with current_app.app_context():
        db.engine.execute('create extension if not exists citext')
        db.create_all()
        stamp()
        create_default_user(parsed.email, parsed.password)
        populate()

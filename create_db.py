import argparse
import getpass
import re

from flask_migrate import stamp

from app import current_app
from app.models import db
from populate_db import populate
from tests.all.integration.auth_helper import create_super_admin


def create_default_user(email, password):
    print("Your login is 'super_admin'.")
    if not email:
        ask_email = True
        while ask_email:
            email = input("Enter email for super_admin    : ")
            if not re.match(r'[^@]+@[^@]+\.[^@]+', email):
                print('\nInvalid email address\n')
                continue
            ask_email = False
      
    if not password:
        ask_password = True
        password_wrongformat=True
        while ask_password:
            while password_wrongformat = True:
                password = getpass.getpass("Enter password for super_admin : ")
                if len(password) < 8:
                    print('\nPassword should have minimum 8 characters')
                    continue
                else:
                    passw = "/^(?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[^a-zA-Z0-9])(?!.*\s).{8,15}$/"
                    if re.match(passw, password) :
                        password_wrongformat = False
                    print('\n Password should contain one lowercase and uppercase letter, one numeric digit and special character")
            repassword = getpass.getpass("Enter your password again to confirm : ")
            if password != repassword:
                print('\nPassword did not match')
                continue
            ask_password = False
    create_super_admin(email, password)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("email", nargs='?', help="The email for super_admin.", default='')
    parser.add_argument("password", nargs='?', help="The password for super_admin.", default='')
    parsed = parser.parse_args()
    with current_app.app_context():
        db.create_all()
        stamp()
        create_default_user(parsed.email, parsed.password)
        populate()

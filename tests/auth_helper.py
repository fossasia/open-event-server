"""Copyright 2015 Rafal Kowalski"""
from flask import url_for

from open_event.helpers.helpers import get_serializer
from open_event.helpers.data import DataManager, save_to_db


def login(app, email, password):
    return app.post('login/',
                    data=dict(
                        email=email,
                        password=password
                    ), follow_redirects=True)


def logout(app):
    return app.get('logout', follow_redirects=True)


def register(app, email, password):
    s = get_serializer()
    data = [email, password]
    data_hash = s.dumps(data)
    app.post(
        url_for('admin.register_view'),
        data=dict(email=email, password=password),
        follow_redirects=True)
    return app.get(
        url_for('admin.create_account_after_confirmation_view', hash=data_hash),
        follow_redirects=True)

def create_super_admin(email, password):
    user = DataManager.create_user([email, password], is_verified=True)
    user.is_super_admin = True
    user.is_admin = True
    save_to_db(user, "User updated")
    return user

def create_user(email, password, is_verified=True):
    """
    Registers the user but not logs in
    """
    DataManager.create_user([email, password], is_verified=is_verified)

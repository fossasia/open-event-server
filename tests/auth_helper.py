"""Copyright 2015 Rafal Kowalski"""
from flask import url_for

from open_event.helpers.helpers import get_serializer


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
    return app.get(url_for('admin.create_account_after_confirmation_view', hash=data_hash), follow_redirects=True)

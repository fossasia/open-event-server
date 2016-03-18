"""Copyright 2015 Rafal Kowalski"""
from flask import url_for


def login(app, login, password):
    return app.post('admin/login/',
                    data=dict(
                        login=login,
                        password=password
                    ), follow_redirects=True)


def logout(app):
    return app.get('admin/logout', follow_redirects=True)


def register(app, login, email, password):
    return app.post('admin/register/',
                    data=dict(
                        login=login,
                        email=email,
                        password=password
                    ), follow_redirects=True)

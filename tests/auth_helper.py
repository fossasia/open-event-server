"""Copyright 2015 Rafal Kowalski"""


def login(app, email, password):
    return app.post('admin/login/',
                    data=dict(
                        email=email,
                        password=password
                    ), follow_redirects=True)


def logout(app):
    return app.get('admin/logout', follow_redirects=True)


def register(app, email, password):
    return app.post('admin/register/',
                    data=dict(
                        email=email,
                        password=password
                    ), follow_redirects=True)

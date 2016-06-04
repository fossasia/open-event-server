"""Copyright 2015 Rafal Kowalski"""


def login(app, username, password):
    return app.post('admin/login/',
                    data=dict(
                        username=username,
                        password=password
                    ), follow_redirects=True)


def logout(app):
    return app.get('admin/logout', follow_redirects=True)


def register(app, username, email, password):
    return app.post('admin/register/',
                    data=dict(
                        username=username,
                        email=email,
                        password=password
                    ), follow_redirects=True)

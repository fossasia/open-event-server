from flask import url_for
from httmock import urlmatch, response

from app.helpers.data import DataManager, save_to_db
from app.helpers.helpers import get_serializer


@urlmatch(netloc='https://www.googleapis.com/userinfo/v2/me')
def google_profile_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {'link':'http://google.com/some_id'}
    return response(200, content, headers, None, 5, request)

@urlmatch(netloc=r'(.*\.)?google\.com$')
def google_auth_mock(url, request):
    headers = {'content-type': 'application/json'}
    content = {
        "access_token":"2YotnFZFEjr1zCsicMWpAA",
        "token_type":"Bearer",
        "expires_in":3600,
        "refresh_token":"tGzv3JOkF0XG5Qx2TlKWIA",
        "example_parameter":"example_value"
    }
    return response(200, content, headers, None, 5, request)

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

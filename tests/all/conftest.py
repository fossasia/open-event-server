import pytest
from flask import _app_ctx_stack as ctx_stack
from flask.globals import request
from flask_jwt_extended.utils import create_access_token

from app.models import db as _db
from tests.all.integration.setup_database import (
    Environment,
    Setup,
    create_app,
    set_settings,
)
from tests.factories.user import UserFactory


@pytest.fixture(scope='module')
def app():
    app = create_app()
    with app.test_request_context():
        yield app


@pytest.fixture(scope='module')
def client(app):
    return app.test_client()


@pytest.fixture(scope='module')
def database(app):
    _db.engine.execute('create extension if not exists citext')
    _db.create_all()
    set_settings(app_name='Open Event', app_environment=Environment.TESTING)
    yield _db
    Setup.drop_db()


@pytest.fixture(scope='module')
def connection(database):
    with database.engine.connect() as conn:
        yield conn


@pytest.fixture(scope='function')
def db(database, connection):
    transaction = connection.begin()

    options = dict(bind=connection, binds={})
    session = database.create_scoped_session(options=options)
    old_session = database._session
    # For proxying session in factories and flask-json-restapi
    database._session = session

    yield database

    session.remove()
    database._session = old_session
    transaction.rollback()


@pytest.fixture
def user(db):
    user = UserFactory(is_admin=False, is_verified=False)
    db.session.commit()

    return user


@pytest.fixture
def admin_user(db):
    user = UserFactory(is_admin=True)
    db.session.commit()

    return user


@pytest.fixture
def jwt(user):
    return {'Authorization': "JWT " + create_access_token(user.id, fresh=True)}


@pytest.fixture
def admin_jwt(admin_user):
    return {'Authorization': "JWT " + create_access_token(admin_user.id, fresh=True)}


@pytest.fixture
def login_context(client):
    "Use only when above methods don't work"
    yield ctx_stack

    ctx_stack.top.jwt = {}
    ctx_stack.top.jwt_user = None

    request.headers = {}


@pytest.fixture
def user_login(login_context, user, jwt):
    login_context.top.jwt = {'identity': user.id}
    request.headers = jwt

    yield user


@pytest.fixture
def admin_login(login_context, admin_user, admin_jwt):
    login_context.top.jwt = {'identity': admin_user.id}
    request.headers = admin_jwt

    yield admin_user

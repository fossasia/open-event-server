import pytest
from app.models import db as _db
from tests.all.integration.setup_database import (
    Setup,
    create_app,
    set_settings,
    Environment,
)


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
    old_session = database.session
    database.session = session

    yield database

    session.remove()
    database.session = old_session
    transaction.rollback()

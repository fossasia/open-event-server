import unittest

from app.models.user import User
from tests.all.integration.auth_helper import create_super_admin
from tests.all.integration.setup_database import Setup, db


def get_or_create_super_admin():
    user = User.query.filter_by(email="test_super_admin@email.com").first()
    if not user:
        user = create_super_admin("test_super_admin@email.com", "test_super_admin")
    return user


class OpenEventLegacyTestCase(unittest.TestCase):
    """Sets up and tears down database on each run of tests
    Only use for those tests where OpenEventTestCase does not work"""

    def setUp(self) -> None:
        self.app = Setup.create_app()

    def tearDown(self) -> None:
        Setup.drop_db()


class OpenEventTestCase(unittest.TestCase):
    """Sets up and tears down database once per class and
    uses nested transaction rollback for each test"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = Setup.create_app()

    @classmethod
    def tearDownClass(cls) -> None:
        Setup.drop_db()

    def setUp(self):
        with self.app.test_request_context():
            self._connection = db.engine.connect()
            self._transaction = self._connection.begin()

            options = dict(bind=self._connection, binds={})
            session = db.create_scoped_session(options=options)
            self._old_session = db.session
            db.session = session

    def tearDown(self):
        with self.app.test_request_context():
            db.session.remove()
            db.session = self._old_session
            self._transaction.rollback()
            self._connection.close()

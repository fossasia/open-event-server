import unittest

from tests.all.integration.setup_database import Setup

from app.models.user import User
from tests.all.integration.auth_helper import create_super_admin


def get_or_create_super_admin():
    user = User.query.filter_by(email="test_super_admin@email.com").first()
    if not user:
        user = create_super_admin("test_super_admin@email.com", "test_super_admin")
    return user


class OpenEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

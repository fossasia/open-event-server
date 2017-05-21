import unittest

from tests.unittests.setup_database import Setup
from app.helpers.data_getter import DataGetter
from tests.unittests.auth_helper import create_super_admin


def get_or_create_super_admin():
    user = DataGetter.get_user_by_email("test_super_admin@email.com")
    if not user:
        user = create_super_admin("test_super_admin@email.com", "test_super_admin")
    return user


class OpenEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

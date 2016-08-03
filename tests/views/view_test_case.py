
from app.helpers.data_getter import DataGetter
from tests import OpenEventTestCase
from tests.auth_helper import create_super_admin, login
from tests.setup_database import Setup
from app import current_app as app

def get_or_create_super_admin():
    user = DataGetter.get_user_by_email("test_super_admin@email.com")
    if not user:
        user = create_super_admin("test_super_admin@email.com", "test_super_admin")
    return user

"""
Extend from this test case if you need a user to be logged in
"""
class OpenEventViewTestCase(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            self.super_admin = get_or_create_super_admin()
            login(self.app, "test_super_admin@email.com", "test_super_admin")

from app import current_app as app
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers import auth
from tests.all.integration.setup_database import Setup
from app.models import db

import unittest


class TestAuthentication(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_load_user(self):
        """Method to test the registered user details"""

        with app.test_request_context():
            auth_manager = auth.AuthManager()
            auth_manager.init_login(app)
            user = create_user(email = 'authtest@gmail.com', password = 'password')
            self.assertEqual(user, db.session.query(User).get(user.id))


if __name__ == '__main__':
    unittest.main()

from app import current_app as app
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers import auth
from tests.all.integration.setup_database import Setup
from app.models import db
from app.models.user import User

from flask_login import login_user, logout_user
import unittest


class TestAuthentication(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_load_user(self):
        """Method to test the registered user details"""

        with app.test_request_context():
            auth_manager = auth.AuthManager()
            auth_manager.init_login(app)
            user = create_user(email='authtest@gmail.com', password='password')
            self.assertEqual(user, db.session.query(User).get(user.id))

    def test_verified_user(self):
        """Method to test if user is verified"""

        with app.test_request_context():
            auth_manager = auth.AuthManager()
            auth_manager.init_login(app)
            user = create_user(email='authtest@gmail.com', password='password')
            user.is_verified = False
            login_user(user)
            self.assertEqual(auth_manager.is_verified_user(), False)

    def test_is_accessible(self):
        """Method to test if user is accessible(authenticated)"""

        with app.test_request_context():
            auth_manager = auth.AuthManager()
            auth_manager.init_login(app)
            user = create_user(email='test@test.com', password='password')
            login_user(user)
            logout_user()
            self.assertEqual(auth_manager.is_accessible(), False)

if __name__ == '__main__':
    unittest.main()

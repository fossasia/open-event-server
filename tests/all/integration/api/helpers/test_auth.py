from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.auth import AuthManager
from app.models import db
from app.models.user import User

from flask_login import login_user, logout_user
import unittest


class TestAuthentication(OpenEventTestCase):

    def test_load_user(self):
        """Method to test the registered user details"""

        with self.app.test_request_context():
            user = create_user(email='authtest@gmail.com', password='password')
            self.assertEqual(user, db.session.query(User).get(user.id))

    def test_verified_user(self):
        """Method to test if user is verified"""

        with self.app.test_request_context():
            user = create_user(email='authtest@gmail.com', password='password')
            user.is_verified = False
            login_user(user)
            self.assertEqual(AuthManager.is_verified_user(), False)

    def test_is_accessible(self):
        """Method to test if user is accessible(authenticated)"""

        with self.app.test_request_context():
            user = create_user(email='test@test.com', password='password')
            login_user(user)
            logout_user()
            self.assertEqual(AuthManager.is_accessible(), False)

    def test_check_auth_admin(self):
        """Method to test proper authentication & admin rights for a user"""

        with self.app.test_request_context():
            user = create_user(email='authtest@gmail.com', password='password')
            user.is_admin = True
            status = AuthManager.check_auth_admin('authtest@gmail.com', 'password')
            self.assertEqual(True, status)

            user = create_user(email='authtest2@gmail.com', password='password')
            user.is_admin = False
            status = AuthManager.check_auth_admin('authtest2@gmail.com', 'password')
            self.assertEqual(False, status)


if __name__ == '__main__':
    unittest.main()

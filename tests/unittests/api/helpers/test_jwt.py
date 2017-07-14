import unittest

from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from app.factories.user import UserFactory
from app.api.helpers.jwt import jwt_authenticate
from app.models import db
from tests.unittests.setup_database import Setup


class TestJWTHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_jwt_authenticate(self):
        with app.test_request_context():
            user = UserFactory()
            db.session.add(user)
            db.session.commit()

            #Valid Authentication
            authenticated_user = jwt_authenticate(user.email, 'password')
            self.assertEqual(authenticated_user.email, user.email)
            
            #Invalid Authentication
            wrong_credential_user = jwt_authenticate(user.email, 'wrong_password')
            self.assertIsNone(wrong_credential_user)


if __name__ == '__main__':
    unittest.main()

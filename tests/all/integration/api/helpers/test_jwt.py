import unittest

from flask_jwt import _default_jwt_encode_handler

from app import current_app as app
from app.api.helpers.jwt import jwt_authenticate, get_identity
from app.factories.event import EventFactoryBasic
from app.factories.user import UserFactory
from app.models import db
from app.api.helpers.db import save_to_db
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase


class TestJWTHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_jwt_authenticate(self):
        """Method to test jwt authentication"""

        with app.test_request_context():
            user = UserFactory()
            save_to_db(user)

            # Valid Authentication
            authenticated_user = jwt_authenticate(user.email, 'password')
            self.assertEqual(authenticated_user.email, user.email)

            # Invalid Authentication
            wrong_credential_user = jwt_authenticate(user.email, 'wrong_password')
            self.assertIsNone(wrong_credential_user)

    def test_get_identity(self):
        """Method to test identity of authenticated user"""

        with app.test_request_context():
            user = UserFactory()
            save_to_db(user)

            event = EventFactoryBasic()
            event.user_id = user.id
            save_to_db(event)

            # Authenticate User
            self.auth = {'Authorization': "JWT " + str(_default_jwt_encode_handler(user), 'utf-8')}

        with app.test_request_context(headers=self.auth):
            self.assertEquals(get_identity().id, user.id)


if __name__ == '__main__':
    unittest.main()

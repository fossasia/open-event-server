import unittest

from flask_jwt_extended import create_access_token

from app.api.helpers.db import save_to_db
from app.api.helpers.jwt import get_identity, jwt_authenticate
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory


class TestJWTHelperValidation(OpenEventTestCase):
    def test_jwt_authenticate(self):
        """Method to test jwt authentication"""

        with self.app.test_request_context():
            user = UserFactory()
            save_to_db(user)

            # Valid Authentication
            authenticated_user = jwt_authenticate(user.email, 'password')
            assert authenticated_user.email == user.email

            # Invalid Authentication
            wrong_credential_user = jwt_authenticate(user.email, 'wrong_password')
            assert wrong_credential_user is None

    def test_get_identity(self):
        """Method to test identity of authenticated user"""

        with self.app.test_request_context():
            user = UserFactory()
            save_to_db(user)

            event = EventFactoryBasic()
            event.user_id = user.id
            save_to_db(event)

            # Authenticate User
            self.auth = {
                'Authorization': "JWT " + create_access_token(user.id, fresh=True)
            }

        with self.app.test_request_context(headers=self.auth):
            assert get_identity().id == user.id


if __name__ == '__main__':
    unittest.main()

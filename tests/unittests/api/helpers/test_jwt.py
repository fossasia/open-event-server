import unittest
from flask_jwt import _default_jwt_encode_handler

from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from app.factories.user import UserFactory
from app.api.helpers.jwt import jwt_authenticate, get_identity
from app.models import db
from tests.unittests.setup_database import Setup
from app.factories.event import EventFactoryBasic


class TestJWTHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_jwt_authenticate(self):
        with app.test_request_context():
            user = UserFactory()
            db.session.add(user)
            db.session.commit()

            # Valid Authentication
            authenticated_user = jwt_authenticate(user.email, 'password')
            self.assertEqual(authenticated_user.email, user.email)

            # Invalid Authentication
            wrong_credential_user = jwt_authenticate(user.email, 'wrong_password')
            self.assertIsNone(wrong_credential_user)

    def test_get_identity(self):
        with app.test_request_context():
            user = UserFactory()
            db.session.add(user)
            db.session.commit()

            event = EventFactoryBasic()
            event.user_id = user.id
            db.session.add(event)
            db.session.commit()

            # Authenticate User
            self.auth = {'Authorization': "JWT " + _default_jwt_encode_handler(user)}

        with app.test_request_context(headers=self.auth):
            self.assertEquals(get_identity().id, user.id)


if __name__ == '__main__':
    unittest.main()

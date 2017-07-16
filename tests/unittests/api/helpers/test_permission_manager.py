import unittest

from flask_jwt import _default_jwt_encode_handler

from app import current_app as app
from app.api.helpers.permission_manager import has_access
from tests.unittests.utils import OpenEventTestCase
from app.factories.user import UserFactory
from app.models import db
from tests.unittests.setup_database import Setup


class TestPermissionManager(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            user = UserFactory()
            db.session.add(user)
            db.session.commit()

            # Authenticate User
            self.auth = {'Authorization': "JWT " + _default_jwt_encode_handler(user)}

    def test_has_access(self):
        with app.test_request_context(headers=self.auth):
            self.assertTrue(has_access('is_admin'))
            self.assertFalse(has_access('is_super_admin'))


if __name__ == '__main__':
    unittest.main()

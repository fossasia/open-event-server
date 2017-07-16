import unittest

from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.errors import ForbiddenError, NotFoundError
from tests.unittests.setup_database import Setup
from app import current_app as app


class TestErrorsHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_errors(self):
        with app.test_request_context():
            # Forbidden Error
            forbidden_error = ForbiddenError({'source': ''}, 'Super admin access is required')
            self.assertEqual(forbidden_error.status, 403)

            # Not Found Error
            not_found_error = NotFoundError({'source': ''}, 'Object not found.')
            self.assertEqual(not_found_error.status, 404)


if __name__ == '__main__':
    unittest.main()

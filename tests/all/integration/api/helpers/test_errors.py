import unittest

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.errors import ForbiddenError, NotFoundError, ServerError, \
    UnprocessableEntityError, BadRequestError
from tests.all.integration.setup_database import Setup
from app import current_app as app


class TestErrorsHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_errors(self):
        """Method to test the status code of all errors."""

        with app.test_request_context():
            # Forbidden Error
            forbidden_error = ForbiddenError({'source': ''}, 'Super admin access is required')
            self.assertEqual(forbidden_error.status, 403)

            # Not Found Error
            not_found_error = NotFoundError({'source': ''}, 'Object not found.')
            self.assertEqual(not_found_error.status, 404)

            # Server Error
            server_error = ServerError({'source': ''}, 'Internal Server Error')
            self.assertEqual(server_error.status, 500)

            # UnprocessableEntity Error
            unprocessable_entity_error = UnprocessableEntityError({'source': ''},
                'Entity cannot be processed')
            self.assertEqual(unprocessable_entity_error.status, 422)

            # Bad Request Error
            bad_request_error = BadRequestError({'source': ''}, 'Request cannot be served')
            self.assertEqual(bad_request_error.status, 400)


if __name__ == '__main__':
    unittest.main()

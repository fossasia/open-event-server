import unittest
import json

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.errors import ErrorResponse, ForbiddenError, NotFoundError, ServerError, \
    UnprocessableEntityError, BadRequestError
from tests.all.integration.setup_database import Setup
from flask_rest_jsonapi.errors import jsonapi_errors
from flask import make_response
from app import current_app as app


class TestErrorsHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_error_response_base_respond(self):
        """Method to test base error response methods"""

        with app.test_request_context():
            base_error_response = ErrorResponse(source="test source", detail="test detail")
            json_object = json.dumps(jsonapi_errors([base_error_response.to_dict()]))
            self.assertNotEqual(base_error_response.respond(), make_response(json_object, 200,
                                {'Content-Type': 'application/vnd.api+json'}))


    def test_errors(self):
        """Method to test the status code of all errors"""

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

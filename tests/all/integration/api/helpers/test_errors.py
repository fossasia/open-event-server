import json
import unittest

from flask import make_response
from flask_rest_jsonapi.errors import jsonapi_errors

from app.api.helpers.errors import ErrorResponse
from tests.all.integration.utils import OpenEventTestCase


class TestErrorsHelperValidation(OpenEventTestCase):
    def test_error_response_base_respond(self):
        """Method to test base error response methods"""

        with self.app.test_request_context():
            base_error_response = ErrorResponse(
                source="test source", detail="test detail"
            )
            json_object = json.dumps(jsonapi_errors([base_error_response.to_dict()]))
            assert base_error_response.respond() != \
                make_response(
                    json_object, 200, {'Content-Type': 'application/vnd.api+json'}
                )


if __name__ == '__main__':
    unittest.main()

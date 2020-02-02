from unittest import TestCase

from app.api.helpers.errors import (
    BadRequestError,
    ErrorResponse,
    ForbiddenError,
    NotFoundError,
    ServerError,
    UnprocessableEntityError,
)


class TestErrorDetails(TestCase):
    """Test for error responses"""

    def test_error_response_dict_details(self):
        """To test details in the form of dict"""

        error_response = ErrorResponse(source="test source", detail="test detail")
        expected_dict = {
            'status': error_response.status,
            'source': error_response.source,
            'title': error_response.title,
            'detail': error_response.detail,
        }
        self.assertEqual(error_response.to_dict(), expected_dict)

    def test_errors(self):
        """Method to test the status code of all errors"""

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
        unprocessable_entity_error = UnprocessableEntityError(
            {'source': ''}, 'Entity cannot be processed'
        )
        self.assertEqual(unprocessable_entity_error.status, 422)

        # Bad Request Error
        bad_request_error = BadRequestError({'source': ''}, 'Request cannot be served')
        self.assertEqual(bad_request_error.status, 400)

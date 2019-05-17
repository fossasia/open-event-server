from unittest import TestCase
from app.api.helpers.errors import ErrorResponse


class TestErrorDetails(TestCase):
    """Test for error responses"""

    def test_error_response_dict_details(self):
        """To test details in the form of dict"""

        error_response = ErrorResponse(source="test source", detail="test detail")
        expected_dict = {'status': error_response.status,
                         'source': error_response.source,
                         'title': error_response.title,
                         'detail': error_response.detail}
        self.assertEqual(error_response.to_dict(), expected_dict)

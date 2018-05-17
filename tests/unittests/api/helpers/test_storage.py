"""Test file for storage functions."""

from app.api.helpers.storage import create_url
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestStorageHelperValidation(OpenEventTestCase):
    """Test class for testing storage helper functions."""

    def setUp(self):
        """Method to set up app for testing."""
        self.app = Setup.create_app()

    def test_create_url(self):
        """Method to test the create_url function."""

        request_url = 'https://localhost:5000'
        file_relative_path = '/some/path/image.png'
        expected_file_url = 'https://localhost:5000/some/path/image.png'

        self.assertEqual(
            create_url(request_url, file_relative_path), expected_file_url
            )
        request_url = 'https://localhost:443'
        expected_file_url = 'https://localhost/some/path/image.png'
        self.assertEqual(
            create_url(request_url, file_relative_path), expected_file_url
            )
        request_url = 'http://localhost:80'
        expected_file_url = 'http://localhost/some/path/image.png'
        self.assertEqual(
            create_url(request_url, file_relative_path), expected_file_url
            )

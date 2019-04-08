"""Test file for storage functions."""
from unittest import TestCase

from app.api.helpers.storage import create_url


class TestStorageHelperValidation(TestCase):
    """Test class for testing storage helper functions."""

    def test_arbitrary_url(self):
        """Method to test a url with arbitrary port."""

        request_url = 'https://localhost:5000'
        expected_file_url = 'https://localhost:5000/some/path/image.png'

        self.assertEqual(
            expected_file_url, create_url(request_url, '/some/path/image.png')
            )

    def test_http_url(self):
        """Method to test a url with port 80."""
        request_url = 'http://localhost:80'
        expected_file_url = 'http://localhost/some/path/image.png'
        self.assertEqual(
            expected_file_url, create_url(request_url, '/some/path/image.png')
            )

    def test_https_url(self):
        """Method to test a url with port 443."""
        request_url = 'https://localhost:443'
        expected_file_url = 'https://localhost/some/path/image.png'
        self.assertEqual(
            expected_file_url, create_url(request_url, '/some/path/image.png')
            )

    def test_create_url(self):
        """Method to test a generated url of uploaded file"""
        request_url = "https://localhost:4200"
        expected_file_url = 'https://localhost:4200/some/path/image.png'
        self.assertEqual(
            expected_file_url, create_url(request_url, '/some/path/image.png')
            )

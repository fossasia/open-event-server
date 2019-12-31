"""Test file for storage functions."""
import os
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from app.api.helpers.storage import create_url, generate_hash, UploadedFile


class TestStorageHelperValidation(unittest.TestCase):
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

    def test_generate_hash(self):
        """Test generation of hash for a key."""

        def patch_settings(settings):
            settings.return_value = {
                'secret': 'secret_key'
            }

        with patch('app.api.helpers.storage.get_settings') as get_settings:
            patch_settings(get_settings)
            test_input = 'case1'
            exepected_output = 'WUFCV0xHVk'
            actual_output = generate_hash(test_input)
            self.assertEqual(exepected_output, actual_output)
            self.assertEqual(len(actual_output), 10)

            test_input = '/static/uploads/pdf/temp/'
            exepected_output = 'MzRueVhjY0'
            actual_output = generate_hash(test_input)
            self.assertEqual(exepected_output, actual_output)
            self.assertEqual(len(actual_output), 10)


class TestUploadedFile(unittest.TestCase):
    test_data = b'\xffhellothere'

    def _uploaded_file(self, folder, filename='testfile.bin'):
        path = os.path.join(folder, filename)
        with open(path, 'wb') as f:
            f.write(self.test_data)
        return UploadedFile(path, filename)

    def test_read(self):
        with TemporaryDirectory() as folder:
            file = self._uploaded_file(folder)
            self.assertEqual(file.read(), self.test_data)


if __name__ == '__main__':
    unittest.main()

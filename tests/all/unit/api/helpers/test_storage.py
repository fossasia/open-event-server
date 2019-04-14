"""Test file for storage functions."""
import unittest
from unittest.mock import patch

from app.api.helpers.storage import create_url, generate_hash, upload_local
from flask import Flask


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

    """Test local file upload."""
    @patch('app.api.helpers.storage.upload_local')
    @patch('app.api.helpers.storage.generate_hash', return_value='hash')
    @patch('app.api.helpers.storage.get_settings', return_value={'static_domain': 'https://next.eventyay.com'})
    @patch('app.api.helpers.storage.UploadedFile')
    def test_upload_local(self, uploadedfile_object, settings, generated_hash, uploadlocal):
        expected_response = 'https://next.eventyay.com/media/upload_key/hash/test.pdf'
        uploadedfile_object.filename = 'test.pdf'

        app = Flask(__name__)
        with app.app_context():
            app.config['BASE_DIR'] = 'testdir'
            actual_response = upload_local(uploadedfile_object, 'upload_key')
            self.assertEqual(expected_response, actual_response)


if __name__ == '__main__':
    unittest.main()

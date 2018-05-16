"""Test file for storage functions."""
import os
from urllib.parse import urljoin, urlparse

from flask import request

from app import current_app as app
from app.api.helpers.storage import generate_hash, UploadedFile, upload_local
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestStorageHelperValidation(OpenEventTestCase):
    """Test class for testing storage helper functions."""

    def setUp(self):
        """Method to set up app for testing."""
        self.app = Setup.create_app()

    def test_upload_local(self):
        """Method to test the upload_local function."""
        test_name = 'image.png'
        test_path = os.path.join(app.config['BASE_DIR'],
                                 'static/media/temp',
                                 test_name
                                 )
        with open(test_path, 'wb') as img_file:
            img_file.write(b'test content')

        upfile = UploadedFile(test_path, 'image.png')
        test_key = 'test_key'

        with app.test_request_context():
            test_hash = generate_hash(test_key)
            test_url = request.url
            upload_url = upload_local(upfile, key=test_key)

        expected_url = urljoin(
            '{url.scheme}://{url.netloc}'.format(url=urlparse(test_url)),
            os.path.join('static/media/',
            test_key,
            test_hash,
            test_name)
            )

        self.assertEqual(upload_url, expected_url)

        os.unlink(test_path)  # Removes the file created for testing.
        os.unlink(os.path.join(app.config['BASE_DIR'],
                               'static/media',
                               test_key,
                               test_hash,
                               test_name
                               )
                )  # Removes the temporary 'uploaded' test file.

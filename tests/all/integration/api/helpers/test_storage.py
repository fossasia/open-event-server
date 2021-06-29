import unittest
from unittest.mock import patch

from app.api.helpers.storage import upload_local
from tests.all.integration.utils import OpenEventTestCase


class TestStorage(OpenEventTestCase):
    """Contains test for Storage Helpers"""

    """Test local file upload."""

    @patch('app.api.helpers.storage.upload_local')
    @patch('app.api.helpers.storage.generate_hash', return_value='hash')
    @patch(
        'app.api.helpers.storage.get_settings',
        return_value={'static_domain': 'https://next.eventyay.com'},
    )
    @patch('app.api.helpers.storage.UploadedFile')
    def test_upload_local(
        self, uploadedfile_object, settings, generated_hash, uploadlocal
    ):
        expected_response = (
            'https://next.eventyay.com/static/media/upload_key/hash/test.pdf'
        )
        uploadedfile_object.filename = 'test.pdf'

        with self.app.test_request_context():
            actual_response = upload_local(uploadedfile_object, 'upload_key')
            assert expected_response == actual_response


if __name__ == '__main__':
    unittest.main()

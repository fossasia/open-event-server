import unittest

from flask import url_for

from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from StringIO import StringIO
from app import current_app as app


class TestImageUpload(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_img_upload(self):
        with app.test_request_context():
            data = dict(
                slides=(StringIO(b'my file contents'), "file1.png"),
                photo=(StringIO(b'my photo contents'), "file2.png")
            )
            response = self.app.post('events/1/session/create/', content_type='multipart/form-data', data=data,
                                     follow_redirects=True)
            self.assertTrue(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()

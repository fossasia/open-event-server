from tests.unittests.utils import OpenEventTestCase
from tests.unittests.setup_database import Setup
from StringIO import StringIO
from app import current_app as app


class TestImageUpload(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_img_upload(self):
        with app.test_request_context():
            data = dict(
                file=(StringIO(b'my file contents'), "file.png"),
            )
            response = self.app.post('/profile/edit/', content_type='multipart/form-data', data=data,
                                     follow_redirects=True)
            self.assertTrue(response.status_code, 200)

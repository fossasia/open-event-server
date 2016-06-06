import unittest
import json
import base64

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.auth_helper import register
from tests.api.utils import create_event, get_path
from tests.api.utils_post_data import *

from open_event import current_app as app


class TestPostApiBasicAuth(OpenEventTestCase):
    """
    Tests the Basic Authorization in Post API
    """
    def setUp(self):
        self.app = Setup.create_app()
        register(self.app, 'myemail@gmail.com', 'test')
        with app.test_request_context():
            create_event()

    def _test_model(self, name, data):
        path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={
                'content-type': 'application/json',
                'Authorization': 'Basic %s' %
                base64.b64encode('myemail@gmail.com:test')
            }
        )
        self.assertNotEqual(response.status_code, 401)
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test' + str(name).title(), response.data)

    # def test_event_api(self):
    #     self._test_model('event', POST_EVENT_DATA)

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_level_api(self):
        self._test_model('level', POST_LEVEL_DATA)

    def test_format_api(self):
        self._test_model('format', POST_FORMAT_DATA)

    def test_language_api(self):
        self._test_model('language', POST_LANGUAGE_DATA)

    # TODO: has some issues with datetime and sqlite
    # def test_session_api(self):
    #     self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)


if __name__ == '__main__':
    unittest.main()

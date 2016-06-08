import unittest
import json

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.auth_helper import login, register
from tests.api.utils import create_event, get_path
from tests.api.utils_post_data import *

from open_event import current_app as app


class TestPostApi(OpenEventTestCase):
    """
    Test POST APIs against 401 (unauthorized) and
    200 (successful) status codes
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            create_event()

    def _login_user(self):
        """
        Registers an email and logs in.
        """
        register(self.app, 'test@example.com', 'test')

    def _test_model(self, name, data):
        """
        Tests -
        1. Without login, try to do a POST request and catch 401 error
        2. Login and match 200 response code and correct response data
        """
        path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )
        self.assertEqual(401, response.status_code, msg=response.data)
        # TODO: has some issues with datetime and sqlite
        # so return in event and session
        if name in ['event', 'session']:
            return
        # login and send the request again
        self._login_user()
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )
        self.assertEqual(200, response.status_code, msg=response.data)
        self.assertIn('Test' + str(name).title(), response.data)
        return response

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA)

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
    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)


if __name__ == '__main__':
    unittest.main()

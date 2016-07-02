import unittest
import json

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path
from tests.api.utils_post_data import *
from tests.auth_helper import register
from open_event import current_app as app


class TestPutApiBase(OpenEventTestCase):
    """
    Base class for help testing PUT APIs
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            create_event()

    def _login_user(self):
        """
        Registers an email and logs in.
        """
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')

    def _put(self, path, data):
        return self.app.put(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )


class TestPutApi(TestPutApiBase):
    """
    Test PUT APIs against 401 (unauthorized) and
    200 (successful) status codes
    """
    def _test_model(self, name, data):
        """
        Tests -
        1. Without login, try to do a PUT request and catch 401 error
        2. Login and match 200 response code and make sure that
            data changed
        """
        self._login_user()
        path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 201)

        path = get_path(1) if name == 'event' else get_path(1, name + 's', 1)
        response = self._put(path, data)
        self.assertEqual(response.status_code, 200, msg=response.data)
        self.assertIn('Test' + str(name).title(), response.data)

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA)

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)


if __name__ == '__main__':
    unittest.main()

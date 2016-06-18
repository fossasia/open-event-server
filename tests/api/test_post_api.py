import unittest
import json

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path
from tests.api.utils_post_data import *
from tests.auth_helper import register
from open_event import current_app as app


class TestPostApiBase(OpenEventTestCase):
    """
    Base class to test POST APIs
    Includes some helper methods which are required by POST API testcases
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

    def post_request(self, path, data):
        """
        send a post request to a url
        """
        return self.app.post(
            path,
            data=json.dumps(data),
            headers={'content-type': 'application/json'}
        )


class TestPostApi(TestPostApiBase):
    """
    Test POST APIs against 401 (unauthorized) and
    201 (successful) status codes
    """
    def _test_model(self, name, data, checks=[]):
        """
        Tests -
        1. Without login, try to do a POST request and catch 401 error
        2. Login and match 201 response code and correct response data
        Param:
            checks - list of strings to assert in successful response data
        """
        path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.post_request(path, data)
        self.assertEqual(401, response.status_code, msg=response.data)
        # login and send the request again
        self._login_user()
        response = self.post_request(path, data)
        self.assertEqual(201, response.status_code, msg=response.data)
        self.assertIn('location', response.headers)
        self.assertIn('Test' + str(name).title(), response.data)
        for string in checks:
            self.assertIn(string, response.data, msg=string)
        return response

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA, ['test@example.com'])

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_session_api_extra_payload(self):
        extraData = POST_SESSION_DATA.copy()
        extraData['new_key_2'] = 'value'
        self._test_model('session', extraData)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)


if __name__ == '__main__':
    unittest.main()

import unittest
import json
import base64

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path, create_sponsor_type
from tests.api.utils_post_data import *
from tests.auth_helper import register
from open_event import current_app as app


class TestPostApiBasicAuth(OpenEventTestCase):
    """
    Tests the Basic Authorization in Post API
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'myemail@gmail.com', u'test')
            event_id = create_event()
            create_sponsor_type(event_id)

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
        self.assertEqual(response.status_code, 201)
        self.assertIn('Test' + str(name).title(), response.data)

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

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)

    def test_sponsor_type_api(self):
        self._test_model('sponsor_type', POST_SPONSOR_TYPE_DATA)


class TestPostApiJWTAuth(TestPostApiBasicAuth):
    """
    Tests the JWT Auth in Post API
    """
    def _send_login_request(self, password):
        """
        sends a login request and returns the response
        """
        response = self.app.post(
            '/api/v2/login',
            data=json.dumps({
                'email': 'myemail@gmail.com',
                'password': password
            }),
            headers={'content-type': 'application/json'}
        )
        return response

    def _test_model(self, name, data):
        """
        1. Test getting JWT token with wrong credentials and getting 401
        2. Get JWT token with right credentials
        3. Send a sample successful POST request
        """
        path = get_path() if name == 'event' else get_path(1, name + 's')
        # get access token
        response = self._send_login_request('wrong_password')
        self.assertEqual(response.status_code, 401)
        response = self._send_login_request('test')
        self.assertEqual(response.status_code, 200)
        token = json.loads(response.data)['access_token']
        # send a post request
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={
                'content-type': 'application/json',
                'Authorization': 'JWT %s' % token
            }
        )
        self.assertNotEqual(response.status_code, 401)
        self.assertEqual(response.status_code, 201)
        self.assertIn('Test' + str(name).title(), response.data)


if __name__ == '__main__':
    unittest.main()

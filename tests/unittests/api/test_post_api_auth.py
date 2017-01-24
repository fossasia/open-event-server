import base64
import json
import unittest

from app import current_app as app
from tests.unittests.api.utils import create_event, get_path
from tests.unittests.api.utils_post_data import *
from tests.unittests.auth_helper import register, logout
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class PostApiAuthTestCase:
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'myemail@gmail.com', u'test')
            create_event(creator_email=u'myemail@gmail.com')
            logout(self.app)

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


class TestPostApiBasicAuth(PostApiAuthTestCase, OpenEventTestCase):
    """
    Tests the Basic Authorization in Post API
    """

    def _test_model(self, name, data):
        with app.test_request_context():
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
            self.assertEqual(response.status_code, 201, response.data)
            self.assertIn('Test' + str(name).title(), response.data)


class TestPostApiJWTAuth(PostApiAuthTestCase, OpenEventTestCase):
    """
    Tests the JWT Auth in Post API
    """

    def _send_login_request(self, password):
        """
        sends a login request and returns the response
        """
        response = self.app.post(
            '/api/v1/login',
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

import unittest
import json

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path
from tests.api.utils_post_data import *
from tests.auth_helper import register
from open_event import current_app as app

from open_event.api.events import EVENT_POST, SOCIAL_LINK_POST
from open_event.api.tracks import TRACK_POST
from open_event.api.microlocations import MICROLOCATION_POST
from open_event.api.sessions import SESSION_POST, SESSION_TYPE_POST
from open_event.api.speakers import SPEAKER_POST
from open_event.api.sponsors import SPONSOR_POST


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
    def _test_model(self, name, data, path=None, checks=[]):
        """
        Tests -
        1. Without login, try to do a POST request and catch 401 error
        2. Login and match 201 response code and correct response data
        Param:
            checks - list of strings to assert in successful response data
        """
        if not path:
            path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.post_request(path, data)
        self.assertEqual(401, response.status_code, msg=response.data)
        # login and send the request again
        self._login_user()
        response = self.post_request(path, data)
        self.assertEqual(201, response.status_code, msg=response.data)
        self.assertIn('location', response.headers)
        self.assertIn('Test' + name[0].upper() + name[1:], response.data)
        for string in checks:
            self.assertIn(string, response.data, msg=string)

    def test_event_api(self):
        self._test_model(
            'event', POST_EVENT_DATA,
            checks=['test@example.com', 'Test licence']
        )

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA)

    def test_session_api_extra_payload(self):
        """
        Test to make sure extra key added in payload is removed
        """
        extraData = POST_SESSION_DATA.copy()
        extraData['new_key_2'] = 'value'
        self._test_model('session', extraData)

    def test_session_api_extended(self):
        self._login_user()
        path = get_path(1, 'tracks')
        self.post_request(path, POST_TRACK_DATA)
        path = get_path(1, 'microlocations')
        self.post_request(path, POST_MICROLOCATION_DATA)
        path = get_path(1, 'speakers')
        self.post_request(path, POST_SPEAKER_DATA)
        # create session json
        data = POST_SESSION_DATA.copy()
        data['track_id'] = 1
        data['microlocation_id'] = 1
        data['speaker_ids'] = [1]
        resp = self.post_request(get_path(1, 'sessions'), data)
        self.assertEqual(resp.status_code, 201)
        for i in ['TestTrack', 'TestSpeaker', 'TestMicrolocation']:
            self.assertIn(i, resp.data, i)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA)

    def test_social_link_api(self):
        self._test_model(
            'socialLink', POST_SOCIAL_LINK_DATA, path=get_path(1, 'links')
        )

    def test_session_type_api(self):
        self._test_model(
            'sessionType', POST_SESSION_TYPE_DATA,
            path=get_path(1, 'sessions', 'types')
        )


class TestPostApiMin(TestPostApiBase):
    """
    Test POST API with minimum payload
    Only required payloads are kept
    """
    def _test_model(self, name, data, api_model, path=None):
        # strip data
        data = data.copy()
        for i in api_model:
            if not api_model[i].required:
                data.pop(i, None)
        # test
        if not path:
            path = get_path() if name == 'event' else get_path(1, name + 's')
        self._login_user()
        response = self.post_request(path, data)
        self.assertEqual(201, response.status_code, msg=response.data)
        self.assertIn('Test' + name[0].upper() + name[1:], response.data)

    def test_event_api(self):
        self._test_model('event', POST_EVENT_DATA, EVENT_POST)

    def test_track_api(self):
        self._test_model('track', POST_TRACK_DATA, TRACK_POST)

    def test_microlocation_api(self):
        self._test_model('microlocation', POST_MICROLOCATION_DATA, MICROLOCATION_POST)

    def test_session_api(self):
        self._test_model('session', POST_SESSION_DATA, SESSION_POST)

    def test_speaker_api(self):
        self._test_model('speaker', POST_SPEAKER_DATA, SPEAKER_POST)

    def test_sponsor_api(self):
        self._test_model('sponsor', POST_SPONSOR_DATA, SPONSOR_POST)

    def test_social_link_api(self):
        self._test_model(
            'socialLink', POST_SOCIAL_LINK_DATA,
            SOCIAL_LINK_POST, path=get_path(1, 'links')
        )

    def test_session_type_api(self):
        self._test_model(
            'sessionType', POST_SESSION_TYPE_DATA,
            SESSION_TYPE_POST, path=get_path(1, 'sessions', 'types')
        )


if __name__ == '__main__':
    unittest.main()

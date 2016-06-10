import unittest
import json


from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path, create_sponsor_type
from tests.api.utils_post_data import *
from tests.auth_helper import register
from open_event import current_app as app

class TestDeleteApi(OpenEventTestCase):
    """
    Test Delete APIs for 200 (successful) status codes
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event_id = create_event()
            create_sponsor_type(event_id)

    def _login_user(self):
        """
        Registers an email and logs in.
        """
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')

    def _test_model(self, name, data):
        """
        Logs in a user and creates model.
        Tests for 200 status on deletion and for the deleted object.
        Tests that the deleted object no longer exists.
        """
        self._login_user()
        path = get_path() if name == 'event' else get_path(1, name + 's')
        response = self.app.post(
            path,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )

        path = get_path(1) if name == 'event' else get_path(1, name + 's', 1)
        response = self.app.delete(
            path,
            data=json.dumps(data),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn('Test' + str(name).title(), response.data)

        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)

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


if __name__ == '__main__':
    unittest.main()

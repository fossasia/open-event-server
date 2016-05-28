import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import get_path, create_event, create_services

from open_event import current_app as app


class TestGetApi(OpenEventTestCase):
    """Tests for version 2 GET APIs
    """

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            # `event_id` is going to be 1
            event_id = create_event()
            # Associate services to event_id
            create_services(event_id)

    def test_event_api(self):
        with app.test_request_context():
            path = get_path()
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestEvent', response.data)
            self.assertEqual(response.status_code, 200)

    def test_track_api(self):
        with app.test_request_context():
            path = get_path(1, 'tracks')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestTrack', response.data)
            self.assertEqual(response.status_code, 200)

    def test_microlocation_api(self):
        with app.test_request_context():
            path = get_path(1, 'microlocations')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestMicrolocation', response.data)
            self.assertEqual(response.status_code, 200)

    def test_level_api(self):
        with app.test_request_context():
            path = get_path(1, 'levels')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestLevel', response.data)
            self.assertEqual(response.status_code, 200)

    def test_format_api(self):
        with app.test_request_context():
            path = get_path(1, 'formats')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestFormat', response.data)
            self.assertEqual(response.status_code, 200)

    def test_language_api(self):
        with app.test_request_context():
            path = get_path(1, 'languages')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestLanguage', response.data)
            self.assertEqual(response.status_code, 200)

    def test_session_api(self):
        with app.test_request_context():
            path = get_path(1, 'sessions')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestSession', response.data)
            self.assertEqual(response.status_code, 200)

    def test_speaker_api(self):
        with app.test_request_context():
            path = get_path(1, 'speakers')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestSpeaker', response.data)
            self.assertEqual(response.status_code, 200)

    def test_sponsor_api(self):
        with app.test_request_context():
            path = get_path(1, 'sponsors')
            response = self.app.get(path, follow_redirects=True)
            self.assertIn('TestSponsor', response.data)
            self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()

import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import get_path, create_event, create_services

from open_event import current_app as app


class TestGetApiListed(OpenEventTestCase):
    """Tests for version 2 Listed GET API endpoints.
    e.g. '/events', '/events/1/tracks', etc.
    """

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            # Create two instances of event/services

            # event_id is going to be 1
            event_id1 = create_event('TestEvent_1')
            # event_id is going to be 2
            create_event('TestEvent_2')

            # Associate services to event_id1
            create_services(event_id1, serial_no=1)
            create_services(event_id1, serial_no=2)

    def _test_path(self, path, service1, service2):
        """Helper function.
        Test response for 200 status code. Also test if response body
        contains event/service name.
        """
        with app.test_request_context():
            response = self.app.get(path, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            self.assertIn(service1, response.data)
            self.assertIn(service2, response.data)

    def test_event_api(self):
        path = get_path()
        self._test_path(path, 'TestEvent_1', 'TestEvent_2')

    def test_track_api(self):
        path = get_path(1, 'tracks')
        self._test_path(path, 'TestTrack1_1', 'TestTrack2_1')

    def test_microlocation_api(self):
        path = get_path(1, 'microlocations')
        self._test_path(path, 'TestMicrolocation1_1', 'TestMicrolocation2_1')

    def test_level_api(self):
        path = get_path(1, 'levels')
        self._test_path(path, 'TestLevel1_1', 'TestLevel2_1')

    def test_format_api(self):
        path = get_path(1, 'formats')
        self._test_path(path, 'TestFormat1_1', 'TestFormat2_1')

    def test_language_api(self):
        path = get_path(1, 'languages')
        self._test_path(path, 'TestLanguage1_1', 'TestLanguage2_1')

    def test_session_api(self):
        path = get_path(1, 'sessions')
        self._test_path(path, 'TestSession1_1', 'TestSession2_1')

    def test_speaker_api(self):
        path = get_path(1, 'speakers')
        self._test_path(path, 'TestSpeaker1_1', 'TestSpeaker2_1')

    def test_sponsor_api(self):
        path = get_path(1, 'sponsors')
        self._test_path(path, 'TestSponsor1_1', 'TestSponsor2_1')


if __name__ == '__main__':
    unittest.main()

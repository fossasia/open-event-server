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

    def _test_path(self, path, *strings):
        """Helper function.
        Test response for 200 status code. Also test if response body
        contains event/service name.
        """
        with app.test_request_context():
            response = self.app.get(path, follow_redirects=True)
            self.assertEqual(response.status_code, 200)
            for string in strings:
                self.assertIn(string, response.data)

    def test_event_api(self):
        path = get_path(1)
        self._test_path(path, 'TestEvent', "'copyright': null")

    def test_track_api(self):
        path = get_path(1, 'tracks', 1)
        self._test_path(path, 'TestTrack_1')

    def test_microlocation_api(self):
        path = get_path(1, 'microlocations', 1)
        self._test_path(path, 'TestMicrolocation_1')

    def test_session_api(self):
        path = get_path(1, 'sessions', 1)
        self._test_path(path, 'TestSession_1')

    def test_speaker_api(self):
        path = get_path(1, 'speakers', 1)
        self._test_path(path, 'TestSpeaker_1')

    def test_sponsor_api(self):
        path = get_path(1, 'sponsors', 1)
        self._test_path(path, 'TestSponsor_1')


if __name__ == '__main__':
    unittest.main()

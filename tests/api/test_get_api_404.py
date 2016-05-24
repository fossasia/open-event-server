from datetime import datetime
import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_path

from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.models.event import Event


class TestGetApiNonExistingEvent(OpenEventTestCase):
    """Test 404 response code for non existing Event
    """

    def test_event_api(self):
        path = create_path(1)
        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)


class TestGetApiNonExistingServices(OpenEventTestCase):
    """Test 404 response code for non existing services.
    Services include Session, Track, Language, etc. (everything except Event)
    """

    def setUp(self):
        """Create Event but don't define services for it.
        """
        self.app = Setup.create_app()
        with app.test_request_context():
            event = Event(name='TestEvent',
                          start_time=datetime(2013, 8, 4, 12, 30, 45),
                          end_time=datetime(2016, 9, 4, 12, 30, 45))
            event.owner = 1

            save_to_db(event, 'Event saved')

    def _test_path(self, path):
        """Helper function.
        Test response for 404 status code. Also test if response body
        contains 'does no exist' string.
        """
        response = self.app.get(path)
        self.assertEqual(response.status_code, 404)
        self.assertIn('does not exist', response.data)


    def test_microlocation_api(self):
        with app.test_request_context():
            path = create_path(1, 'microlocations', 1)
            self._test_path(path)

    def test_track_api(self):
        with app.test_request_context():
            path = create_path(1, 'tracks', 1)
            self._test_path(path)

    def test_level_api(self):
        with app.test_request_context():
            path = create_path(1, 'levels', 1)
            self._test_path(path)

    def test_format_api(self):
        with app.test_request_context():
            path = create_path(1, 'formats', 1)
            self._test_path(path)

    def test_language_api(self):
        with app.test_request_context():
            path = create_path(1, 'languages', 1)
            self._test_path(path)

    def test_session_api(self):
        with app.test_request_context():
            path = create_path(1, 'sessions', 1)
            self._test_path(path)

    def test_speaker_api(self):
        with app.test_request_context():
            path = create_path(1, 'speakers', 1)
            self._test_path(path)

    def test_sponsor_api(self):
        with app.test_request_context():
            path = create_path(1, 'sponsors', 1)
            self._test_path(path)


if __name__ == '__main__':
    unittest.main()

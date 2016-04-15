"""Copyright 2015 Rafal Kowalski"""
import unittest

from tests.set_up import Setup

from open_event import current_app as app
from open_event.helpers.data import save_to_db
from tests.object_mother import ObjectMother

class TestApi(unittest.TestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_api_tracks(self):
        with self.assertRaises(Exception) as context:
            self.app.get('/api/v1/event/1')
        self.assertTrue(AttributeError, context.exception)
        event = ObjectMother.get_event()
        track = ObjectMother.get_track()
        with app.test_request_context():
            save_to_db(event, "Event saved")
            save_to_db(track, "Track saved")
        self.assertEqual(self.app.get('/api/v1/event/1').status_code, 200)
        self.assertEqual(self.app.get('/api/v1/event/1/tracks').status_code, 200)

if __name__ == '__main__':
    unittest.main()

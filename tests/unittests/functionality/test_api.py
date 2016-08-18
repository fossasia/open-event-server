"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.unittests.utils import OpenEventTestCase


from app import current_app as app
from app.helpers.data import save_to_db
from tests.unittests.object_mother import ObjectMother


class TestApi(OpenEventTestCase):

    def test_api_tracks(self):
        with app.test_request_context():
            self.assertEqual(self.app.get('/api/v1/event/1').status_code, 404)
            event = ObjectMother.get_event()
            track = ObjectMother.get_track()

            save_to_db(event, "Event saved")
            save_to_db(track, "Track saved")
        self.assertEqual(self.app.get('/api/v1/event/1').status_code, 200)
        self.assertEqual(self.app.get('/api/v1/event/1/tracks').status_code, 200)

if __name__ == '__main__':
    unittest.main()

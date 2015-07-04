"""Copyright 2015 Rafal Kowalski"""
import unittest
from flask import url_for
from setup_database import Setup
from open_event import app
from open_event.helpers.data import save_to_db
from object_mother import ObjectMother
from auth_helper import register
from open_event.models.track import Track


class TestEvent(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.owner = 1
            track = ObjectMother.get_track()
            save_to_db(event,"Event saved")
            save_to_db(track, "Track saved")
            register(self.app,'test', 'email@gmail.com', 'test')

    def tearDown(self):
        Setup.drop_db()

    def test_api_tracks(self):
        self.assertEqual(self.app.get('/get/api/v1/event/1/tracks').status_code, 200)

    def test_admin_track(self):
        self.assertEqual(self.app.get('/admin/event/1/track').status_code, 200)

    def test_adding_track_by_owner(self):
        with app.test_request_context():
            self.app.post(url_for('event.event_track_new',
                                  event_id=1),
                                  data=dict(
                                      name='track1',
                                      description='trackdescription'),
                                  follow_redirects=True)
            self.assertEqual(len(Track.query.all()), 2)


if __name__ == '__main__':
    unittest.main()

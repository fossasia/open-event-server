import unittest

from open_event.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from open_event import current_app as app

class TestGuestEventPage(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_published_event_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.state = 'Published'
            save_to_db(event, "Event Saved")
            rv = self.app.get('e/' + str(event.id), follow_redirects=True)
            self.assertTrue("Open Event" in rv.data, msg=rv.data)

    def test_unpublished_event_view_attempt(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event Saved")
            rv = self.app.get('e/' + str(event.id), follow_redirects=True)
            self.assertEqual(rv.status_code, 404)

    def test_published_event_sessions_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.state = 'Published'
            save_to_db(event, "Event Saved")
            track = ObjectMother.get_track()
            track.event_id = event.id
            save_to_db(track, "Track Saved")
            speaker = ObjectMother.get_speaker()
            speaker.event_id = event.id
            save_to_db(speaker, "Speaker Saved")
            session = ObjectMother.get_session()
            session.event_id = event.id
            session.speakers = [speaker]
            save_to_db(speaker, "Session Saved")
            rv = self.app.get('e/' + str(event.id) + '/sessions/', follow_redirects=True)
            self.assertTrue("Sessions" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

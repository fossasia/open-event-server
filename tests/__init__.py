"""Written by - Rafal Kowalski"""
import datetime
import unittest
from tests.setup import Setup
from open_event import app
from open_event.models import db
from open_event.models.track import Track
from open_event.models.event import Event


class OpenEventTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_urls_response(self):
        expected_status_code = 200
        urls = [('/get/api/v1/event',),
                ('/admin/sponsor/new/',),
                ('/admin/speaker/new/',),
                ('/admin/session/new/',),
                ('/admin/event/new/',),
                ('/admin/track/new/',),
                ('/admin/microlocation/',),
                ('/admin/sponsor/',),
                ('/admin/speaker/',),
                ('/admin/session/',),
                ('/admin/apiview/',),
                ('/admin/event/',),
                ('/admin/track/',)]
        for url in urls:
            response = self.app.get(url[0])
            self.assertEqual(response.status_code, expected_status_code)

    def test_api_tracks(self):
        with self.assertRaises(Exception) as context:
            self.app.get('/get/api/v1/event/1')
        self.assertTrue(AttributeError, context.exception)
        ev = Event(name="event1", start_time=datetime.datetime(2003, 8, 4, 12, 30, 45), end_time=datetime.datetime(2003, 8, 4, 12, 30, 45))
        tr = Track(name="name", event_id=1, description="description")
        with app.app_context():
            db.session.add(ev)
            db.session.add(tr)
            db.session.commit()
        self.assertEqual(self.app.get('/get/api/v1/event/1').status_code, 200)
        self.assertEqual(self.app.get('/get/api/v1/event/1/tracks').status_code, 200)

if __name__ == '__main__':
    unittest.main()

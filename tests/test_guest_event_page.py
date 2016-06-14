import unittest
from datetime import datetime

from open_event.helpers.data import save_to_db
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from tests.object_mother import ObjectMother
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.auth_helper import register, logout, login
from open_event import current_app as app

class TestMySession(OpenEventTestCase):
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

if __name__ == '__main__':
    unittest.main()

import unittest
from tests.unittests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db
from tests.unittests import OpenEventTestCase
from tests.unittests.auth_helper import login
from tests.unittests.setup_database import Setup
from tests.unittests.utils import get_or_create_super_admin


class TestSessionApi(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            self.super_admin = get_or_create_super_admin()
            login(self.app, "test_super_admin@email.com", "test_super_admin")

    def test_add_session_to_db(self):
        with app.test_request_context():
            # create event
            event = ObjectMother.get_event()
            save_to_db(event, 'Event saved')
            # test
            session = ObjectMother.get_session()
            save_to_db(session, "Session saved")
            self.assertEqual(session.id, 1)
            self.assertEqual(session.event_id, 1)


if __name__ == '__main__':
    unittest.main()

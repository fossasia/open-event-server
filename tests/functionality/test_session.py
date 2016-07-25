"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.auth_helper import login
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db

from tests.views.view_test_case import OpenEventViewTestCase


class TestSessionApi(OpenEventViewTestCase):

    def test_add_session_to_db(self):
        session = ObjectMother.get_session()
        with app.test_request_context():
            save_to_db(session, "Session saved")
            self.assertEqual(session.id, 1)
            self.assertEqual(session.event_id, 1)

if __name__ == '__main__':
    unittest.main()

"""Copyright 2015 Rafal Kowalski"""
import unittest

from setup_database import Setup
from object_mother import ObjectMother
from open_event import app
from open_event.helpers.data import save_to_db


class TestSessionApi(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_add_session_to_db(self):
        session = ObjectMother.get_session()
        with app.test_request_context():
            save_to_db(session, "Session saved")
            self.assertEqual(session.id, 1)

if __name__ == '__main__':
    unittest.main()

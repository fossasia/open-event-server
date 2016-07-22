import unittest
from datetime import datetime
from tests.auth_helper import login
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db
from flask import url_for
from app.models.event import Event
from app.helpers.data import DataManager, trash_session, restore_event, restore_session, restore_user
from app.models.user import User
from app.models.session import Session

class TestAdminTrash(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_restore_event_from_trash(self):
        event = Event(name="event1",
                      start_time=datetime(2003, 8, 4, 12, 30, 45),
                      end_time=datetime(2003, 9, 4, 12, 30, 45),
                      in_trash=True)
        with app.test_request_context():
            save_to_db(event, "Event saved")
            restore_event(1)
            self.assertEqual(event.in_trash, False)

    def test_restore_user_from_trash(self):
        user = User(password="test",
                    email="email@gmail.com",
                    in_trash=True)
        with app.test_request_context():
            save_to_db(user, "User saved")
            restore_user(1)
            self.assertEqual(user.in_trash, False)

    def test_restore_session_from_trash(self):
        event = ObjectMother.get_event()
        session = Session(title='Session 1',
                          long_abstract='dsad',
                          start_time=datetime(2003, 8, 4, 12, 30, 45),
                          end_time=datetime(2003, 8, 4, 12, 30, 45),
                          event_id=1,
                          state='pending',
                          in_trash=True)
        with app.test_request_context():
            save_to_db(event, "Event saved")
            save_to_db(session, "Session saved")
            restore_session(1)
            self.assertEqual(session.in_trash, False)

if __name__ == '__main__':
    unittest.main()

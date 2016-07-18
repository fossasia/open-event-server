import unittest
from datetime import datetime
from tests.auth_helper import register, login
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from flask import url_for
from app.models.event import Event
from app.helpers.data import DataManager, trash_user, trash_session
from app.models.user import User
from app.models.session import Session

class TestAdminTrash(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_event_to_trash(self):
        event = Event(name="event1",
                      start_time=datetime(2003, 8, 4, 12, 30, 45),
                      end_time=datetime(2003, 9, 4, 12, 30, 45),
                      in_trash=False)
        with app.test_request_context():
            save_to_db(event, "Event saved")
            DataManager.trash_event(1)
            url= url_for('events.index_view')
            rv = self.app.get(url)
            self.assertFalse('event1' in rv.data)
            self.assertEqual(event.in_trash, True)

    def test_add_user_to_trash(self):
        user = User(password="test",
                    email="email@gmail.com",
                    in_trash=False)
        with app.test_request_context():
            save_to_db(user, "User saved")
            trash_user(1)
            self.assertEqual(user.in_trash, True)

    def test_add_session_to_trash(self):
        event = ObjectMother.get_event()
        session = Session(title='Session 1',
                          long_abstract='dsad',
                          start_time=datetime(2003, 8, 4, 12, 30, 45),
                          end_time=datetime(2003, 8, 4, 12, 30, 45),
                          event_id=1,
                          state='pending',
                          in_trash=False)
        with app.test_request_context():
            save_to_db(event, "Event saved")
            save_to_db(session, "Session saved")
            trash_session(1)
            url = url_for('event_sessions.index_view', event_id=1)
            rv = self.app.get(url)
            self.assertFalse('Session 1' in rv.data)
            self.assertEqual(session.in_trash, True)

if __name__ == '__main__':
    unittest.main()

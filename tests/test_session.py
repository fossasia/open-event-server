"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.models.session import Session
from datetime import datetime
from flask import url_for


class TestSessionApi(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_session_to_db(self):
        session = ObjectMother.get_session()
        with app.test_request_context():
            save_to_db(session, "Session saved")
            self.assertEqual(session.id, 1)
            self.assertEqual(session.event_id, 1)

    def test_multiple_sessions_for_same_event(self):
        session1 = ObjectMother.get_session()
        session2 = Session(title='test2',
                           long_abstract='dsadsd',
                           start_time=datetime(2003, 8, 4, 12, 30, 45),
                           end_time=datetime(2003, 8, 4, 12, 30, 45),
                           event_id=1,
                           state='pending')
        self.assertEqual(session1.event_id, 1)
        self.assertEqual(session2.event_id, 1)

    def test_session_accept(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('session.accept_session', event_id=1, session_id=1)
            self.assertTrue('accepted' in self.app.get(url, follow_redirects=True).data)

    def test_session_reject(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('session.reject_session', event_id=1, session_id=1)
            self.assertTrue('rejected' in self.app.get(url, follow_redirects=True).data)


if __name__ == '__main__':
    unittest.main()

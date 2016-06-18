"""Copyright 2015 Rafal Kowalski"""
import unittest
from open_event.helpers.permission_decorators import can_accept_and_reject
from tests.auth_helper import register, login
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

    def login(self):
        register(self.app, u'email2@gmail.com', u'test2')
        login(self.app, 'email2@gmail.com', 'test2')

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
            self.login()
            session = ObjectMother.get_session()
            user = ObjectMother.get_user()
            save_to_db(user, "User saved")
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.accept_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("accepted" in rv.data, msg=rv.data)

    def test_session_reject(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            self.login()
            user = ObjectMother.get_user()
            save_to_db(user, "User saved")
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.reject_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("rejected" in rv.data, msg=rv.data)

    def test_session_delete(self):
        with app.test_request_context():
            self.login()
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.delete_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("deleted" in rv.data, msg=rv.data)

    def test_session_view(self):
        with app.test_request_context():
            self.login()
            event = ObjectMother.get_event()
            save_to_db(event)
            session = ObjectMother.get_session()
            session.event_id = event.id
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.session_display_view', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Short Abstract" in rv.data, msg=rv.data)

    def test_wrong_form_config(self):
        with app.test_request_context():
            self.login()
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('event_sessions.create_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Speaker and Session forms have been incorrectly configured for this event."
                            " Session creation has been disabled" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

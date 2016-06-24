"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from flask import url_for

from tests.views.view_test_case import OpenEventViewTestCase


class TestSessionApi(OpenEventViewTestCase):

    def test_session_accept(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.accept_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("The session has been accepted" in rv.data, msg=rv.data)

    def test_session_reject(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.reject_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("The session has been rejected" in rv.data, msg=rv.data)

    def test_session_delete(self):
        with app.test_request_context():
            session = ObjectMother.get_session()
            save_to_db(session, "Session Saved")
            url = url_for('event_sessions.delete_session', event_id=1, session_id=1)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("deleted" in rv.data, msg=rv.data)

    def test_session_view(self):
        with app.test_request_context():
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
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('event_sessions.create_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("incorrectly configured" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

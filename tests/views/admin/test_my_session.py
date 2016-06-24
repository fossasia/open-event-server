import unittest
from datetime import datetime

from open_event.helpers.data import save_to_db
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from tests.auth_helper import logout, login
from tests.object_mother import ObjectMother
from open_event import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase


class TestMySession(OpenEventViewTestCase):

    def test_my_session_detail(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            speaker = Speaker(name="name",
                              email="email2@gmail.com",
                              organisation="FOSSASIA",
                              event_id=event.id,
                              user=self.super_admin,
                              country="India")
            save_to_db(speaker, "Speaker saved")
            session = Session(title='test',
                              long_abstract='dsad',
                              start_time=datetime(2003, 8, 4, 12, 30, 45),
                              end_time=datetime(2003, 8, 4, 12, 30, 45),
                              event_id=event.id,
                              speakers=[speaker],
                              state='pending')
            save_to_db(session, "Session saved")
            rv = self.app.get('events/mysessions/' + str(session.id), follow_redirects=True)
            self.assertTrue("mysessions" in rv.data, msg=rv.data)

    def test_my_session_unauthorized_access(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            user = ObjectMother.get_user()
            save_to_db(user, "User saved")
            save_to_db(event, "Event saved")
            speaker = Speaker(name="name",
                              email="email2@gmail.com",
                              organisation="FOSSASIA",
                              event_id=event.id,
                              user=user,
                              country="India")
            save_to_db(speaker, "Speaker saved")
            session = Session(title='test',
                              long_abstract='dsad',
                              start_time=datetime(2003, 8, 4, 12, 30, 45),
                              end_time=datetime(2003, 8, 4, 12, 30, 45),
                              event_id=event.id,
                              speakers=[speaker],
                              state='pending')
            save_to_db(session, "Session saved")
            rv = self.app.get('events/mysessions/' + str(session.id), follow_redirects=True)
            self.assertEqual(rv.status_code, 404)

    def test_my_session_list(self):
        with app.test_request_context():
            rv = self.app.get('events/mysessions/', follow_redirects=True)
            self.assertTrue("My Session Proposals" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

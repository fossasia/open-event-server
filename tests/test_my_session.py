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

    def test_my_session_detail(self):
        with app.test_request_context():
            speaker = Speaker(name="name",
                              email="email2@gmail.com",
                              organisation="FOSSASIA",
                              country="India")
            save_to_db(speaker, "Speaker saved")
            event = ObjectMother.get_event()
            save_to_db(event, "Event Saved")
            session = Session(title='test',
                              description='dsad',
                              start_time=datetime(2003, 8, 4, 12, 30, 45),
                              end_time=datetime(2003, 8, 4, 12, 30, 45),
                              event_id=event.id,
                              speakers=[speaker],
                              state='pending')
            save_to_db(session, "Session saved")
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            rv = self.app.get('events/mysessions/' + str(session.id), follow_redirects=True)
            logout(self.app)
            self.assertTrue("Description" in rv.data, msg=rv.data)

    def test_my_session_unauthorized_access(self):
        with app.test_request_context():
            speaker = Speaker(name="name",
                              email="email2@gmail.com",
                              organisation="FOSSASIA",
                              country="India")
            save_to_db(speaker, "Speaker saved")
            session = Session(title='test',
                              description='dsad',
                              start_time=datetime(2003, 8, 4, 12, 30, 45),
                              end_time=datetime(2003, 8, 4, 12, 30, 45),
                              event_id=1,
                              speakers=[speaker],
                              state='pending')
            save_to_db(session, "Session saved")
            register(self.app, u'email3@gmail.com', u'test3')
            login(self.app, 'email3@gmail.com', 'test3')
            rv = self.app.get('events/mysessions/' + str(session.id), follow_redirects=True)
            self.assertEqual(rv.status_code, 404)

    def test_my_session_list(self):
        with app.test_request_context():
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            rv = self.app.get('events/mysessions/', follow_redirects=True)
            logout(self.app)
            self.assertTrue("My Session Proposals" in rv.data, msg=rv.data)


if __name__ == '__main__':
    unittest.main()

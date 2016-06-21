import unittest
from tests.utils import OpenEventTestCase
from open_event.models.session_type import SessionType
from open_event.models.session import Session
from tests.setup_database import Setup
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from datetime import datetime


class TestSessionType(OpenEventTestCase):
    def test_add_session_type_to_db(self):
        """Checks the one to many relationship between event and session_types and
                the many to one relationship between session and session_types"""
        self.app = Setup.create_app()
        with app.test_request_context():
            event = ObjectMother.get_event()
            session1 = ObjectMother.get_session()
            session_type1 = SessionType(name='Type1', length='30', event_id='1')
            session_type2 = SessionType(name='Type2', length='30', event_id='1')
            session2 = Session(title='test2',
                               long_abstract='dsadsd',
                               start_time=datetime(2003, 8, 4, 12, 30, 45),
                               end_time=datetime(2003, 8, 4, 12, 30, 45),
                               session_type=session_type1)
            save_to_db(event, "Event Saved")
            save_to_db(session1, "Session1 Saved")
            save_to_db(session2, "Session2 Saved")
            save_to_db(session_type1, "SessionType1 Saved")
            save_to_db(session_type2, "SessionType2 Saved")
            self.assertEqual(session_type1.event_id, 1)
            self.assertEqual(session_type2.event_id, 1)
            self.assertEqual(session2.session_type_id, 1)
            self.assertEqual(session1.session_type_id, None)


if __name__ == '__main__':
    unittest.main()

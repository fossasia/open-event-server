import unittest
from tests.unittests.object_mother import ObjectMother
from app import current_app as app
from app.helpers.data import save_to_db

from tests.unittests.views.view_test_case import OpenEventViewTestCase


class TestSessionApi(OpenEventViewTestCase):

    def test_add_session_to_db(self):
        with app.test_request_context():
            # create event
            event = ObjectMother.get_event()
            save_to_db(event, 'Event saved')
            # test
            session = ObjectMother.get_session()
            save_to_db(session, "Session saved")
            self.assertEqual(session.id, 1)
            self.assertEqual(session.event_id, 1)


if __name__ == '__main__':
    unittest.main()

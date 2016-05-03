import unittest
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db


class TestGetSessionById(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_get_session_by_id(self):
        session = ObjectMother.get_session()
        with app.test_request_context():
            save_to_db(session, "Session saved")
            response = self.app.get('/api/v1/event/sessions/1')
            self.assertEqual(response.status_code,200)

if __name__ == '__main__':
    unittest.main()

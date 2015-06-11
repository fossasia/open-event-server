"""Written by - Rafal Kowalski"""
import datetime
import unittest
from setup import Setup
from open_event import app
from open_event.models import db
from open_event.models.session import Session



class OpenEventTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_add_session_to_db(self):
        session = Session(title='test', description='dsad', start_time=datetime.datetime(2003, 8, 4, 12, 30, 45), end_time=datetime.datetime(2003, 8, 4, 12, 30, 45))

        with app.app_context():
            db.session.add(session)
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
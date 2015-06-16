"""Copyright 2015 Rafal Kowalski"""
import datetime
import unittest
import logging

from setup_database import Setup

from open_event import app
from open_event.models import db
from open_event.models.session import Session



class TestSessionApi(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def tearDown(self):
        Setup.drop_db()

    def test_add_session_to_db(self):
        session = Session(title='test', description='dsad', start_time=datetime.datetime(2003, 8, 4, 12, 30, 45), end_time=datetime.datetime(2003, 8, 4, 12, 30, 45))
        with app.app_context():
            db.session.add(session)
            try:
                db.session.commit()
            except Exception as error:
                logging.error(error)
            self.assertEqual(session.id, 1)

if __name__ == '__main__':
    unittest.main()
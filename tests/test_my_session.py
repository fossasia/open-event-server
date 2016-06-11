"""Copyright 2015 Rafal Kowalski"""
import unittest

from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.auth_helper import register, logout, login
from open_event import current_app as app

class TestMySession(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_my_session_list(self):
        with app.test_request_context():
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            rv = self.app.get('events/mysessions/', follow_redirects=True)
            logout(self.app)
            self.assertTrue("My Session Proposals" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

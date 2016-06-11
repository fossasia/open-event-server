"""Copyright 2015 Rafal Kowalski"""
import unittest

from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.auth_helper import register, logout, login
from open_event import current_app as app


class TestLogin(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_login_page_loads(self):
        rv = self.app.get('login', follow_redirects=True)
        self.assertTrue("Login Form" in rv.data)

    def test_correct_login(self):
        with app.test_request_context():
            register(self.app, u'email@gmail.com', u'test')
            logout(self.app)
            rv = login(self.app, 'email@gmail.com', 'test')
            self.assertTrue("Create event" in rv.data, msg=rv.data)

    def test_incorrect_login(self):
        with app.test_request_context():
            register(self.app, u'email@gmail.com', u'test')
            logout(self.app)
            rv = login(self.app, 'other_email@gmail.com', 'other_test')
            self.assertTrue("Login Form" in rv.data)

    def test_registration(self):
        with app.test_request_context():
            rv = register(self.app, u'email@gmail.com', u'test')
            self.assertTrue("Create event" in rv.data)

    def test_logout(self):
        login(self.app, 'email@gmail.com', 'test')
        rv = logout(self.app)
        self.assertTrue("Login" in rv.data)


if __name__ == '__main__':
    unittest.main()

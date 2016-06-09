"""Copyright 2015 Rafal Kowalski"""
import unittest
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.auth_helper import register, logout, login


class TestLogin(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_login_page_loads(self):
        rv = self.app.get('admin/login', follow_redirects=True)
        self.assertTrue("Login Form" in rv.data)

    def test_correct_login(self):
        register(self.app, 'email@gmail.com', 'test')
        logout(self.app)
        rv = login(self.app, 'email@gmail.com', 'test')
        self.assertTrue("Create New Event" in rv.data)

    def test_incorrect_login(self):
        register(self.app, 'email@gmail.com', 'test')
        logout(self.app)
        rv = login(self.app, 'other_email@gmail.com', 'other_test')
        self.assertTrue("Login Form" in rv.data)

    def test_registration(self):
        rv = register(self.app, 'email@gmail.com', 'test')
        self.assertTrue("Create New Event" in rv.data)

    def test_logout(self):
        login(self.app, 'email@gmail.com', 'test')
        rv = logout(self.app)
        self.assertTrue("Login" in rv.data)


if __name__ == '__main__':
    unittest.main()

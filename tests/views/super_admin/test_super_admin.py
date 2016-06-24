import unittest
from datetime import datetime

from flask import url_for

from open_event.helpers.data import save_to_db
from open_event.models.session import Session
from open_event.models.speaker import Speaker
from tests.auth_helper import logout, login, register_login, register
from tests.object_mother import ObjectMother
from open_event import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase


class TestSuperAdmin(OpenEventViewTestCase):
    def test_admin_dashboard(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin.index_view'), follow_redirects=True)
            self.assertTrue("Dashboard" in rv.data, msg=rv.data)

    def test_admin_dashboard_attempt(self):
        with app.test_request_context():
            logout(self.app)
            register(self.app, "HelloUser@hello.com", "SomeRandomPassword")
            login(self.app, "HelloUser@hello.com", "SomeRandomPassword")
            rv = self.app.get(url_for('sadmin.index_view'), follow_redirects=True)
            self.assertEqual(rv.status_code, 403)

if __name__ == '__main__':
    unittest.main()

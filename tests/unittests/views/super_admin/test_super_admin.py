import unittest

from flask import url_for

from tests.unittests.auth_helper import logout, login, register
from app import current_app as app
from tests.unittests.views.view_test_case import OpenEventViewTestCase


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

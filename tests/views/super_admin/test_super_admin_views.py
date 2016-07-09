import unittest

from flask import url_for

from open_event import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase
from tests.object_mother import ObjectMother
from open_event.helpers.data import save_to_db


class TestSuperAdminViews(OpenEventViewTestCase):
    def test_admin_admin(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            rv = self.app.get(url_for('sadmin_events.index_view'), follow_redirects=True)
            self.assertTrue('event1' in rv.data, msg=rv.data)

    def test_admin_events(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin_events.index_view'), follow_redirects=True)
            self.assertTrue("Manage All Events" in rv.data, msg=rv.data)

    def test_admin_users(self):
        with app.test_request_context():
            user = ObjectMother.get_user()
            save_to_db(user, "User saved")
            rv = self.app.get(url_for('sadmin_users.index_view'), follow_redirects=True)
            self.assertTrue('email@gmail.com' in rv.data, msg=rv.data)

    def test_admin_logs(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin_logs.index_view'), follow_redirects=True)
            self.assertTrue("See System Logs" in rv.data, msg=rv.data)

    def test_admin_my_sessions(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin_sessions.display_my_sessions_view'), follow_redirects=True)
            self.assertTrue("Manage All Sessions" in rv.data, msg=rv.data)

    def test_admin_permissions(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin_permissions.index_view'), follow_redirects=True)
            self.assertTrue("Manage All Permissions" in rv.data, msg=rv.data)

    def test_admin_settings(self):
        with app.test_request_context():
            rv = self.app.get(url_for('sadmin_settings.index_view'), follow_redirects=True)
            self.assertTrue("Manage All Settings" in rv.data, msg=rv.data)


if __name__ == '__main__':
    unittest.main()

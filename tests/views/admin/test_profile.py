import unittest

from flask import url_for

from open_event import current_app as app
from open_event.models.notifications import Notification
from open_event.helpers.data import DataManager
from tests.views.view_test_case import OpenEventViewTestCase, get_or_create_super_admin


class TestProfile(OpenEventViewTestCase):
    def test_profile_view(self):
        with app.test_request_context():
            rv = self.app.get(url_for('profile.index_view'), follow_redirects=True)
            self.assertTrue("test_super_admin@email.com" in rv.data, msg=rv.data)

    def test_profile_edit(self):
        with app.test_request_context():
            data = {
                'email': self.super_admin.email,
                'full_name': 'Super Hero',
                'facebook': 'https://fb.me/super_hero',
                'contact': '+9622100100',
                'twitter': 'https://t.co/super_hero',
                'details': 'I am a super hero'
            }
            rv = self.app.post(url_for('profile.edit_view'), follow_redirects=True, buffered=True,
                               content_type='multipart/form-data', data=data)
            self.assertIn("Super Hero", rv.data, msg=rv.data)

    def test_notifications(self):
        with app.test_request_context():
            user = get_or_create_super_admin()
            notif_title = 'Test Notif Title'
            notif_msg = 'Test Notif Message'
            DataManager.create_user_notification(user=user,
                                                 title=notif_title,
                                                 message=notif_msg)

            rv = self.app.get(url_for('profile.notifications_view'))
            self.assertIn(notif_title, rv.data, msg=rv.data)
            self.assertIn(notif_msg, rv.data, msg=rv.data)

    def test_notification_read(self):
        with app.test_request_context():
            user = get_or_create_super_admin()
            notif_title = 'Test Notif Title'
            notif_msg = 'Test Notif Message'
            DataManager.create_user_notification(user=user,
                                                 title=notif_title,
                                                 message=notif_msg)

            notification = Notification.query.filter_by(user=user,
                                                        title=notif_title,
                                                        message=notif_msg).first()

            rv = self.app.get(url_for('profile.mark_notification_as_read',
                                      notification_id=notification.id))

            self.assertEqual(notification.has_read, True, msg=rv.data)


if __name__ == '__main__':
    unittest.main()

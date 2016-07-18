import json
import unittest

from flask import url_for

from app.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from app import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase
from app.helpers.data_getter import DataGetter

def basic_setup(super_admin):
    event = ObjectMother.get_event()
    save_to_db(event, "Event saved")
    session = ObjectMother.get_session(event.id)
    save_to_db(session, "Session saved")
    speaker = ObjectMother.get_speaker()
    speaker.event_id = event.id
    speaker.user_id = super_admin.id
    save_to_db(speaker, "Speaker saved")
    return event

email_fields = ['session_accept_reject', 'session_schedule', 'next_event', 'new_paper', 'session_schedule']

def asset_notification(self, notification, value):
    for field in email_fields:
        self.assertEqual(getattr(notification, field), value)

class TestSettings(OpenEventViewTestCase):
    def test_email_settings_view(self):
        with app.test_request_context():
            rv = self.app.get(url_for('settings.email_preferences_view'), follow_redirects=True)
            self.assertTrue("Email Preferences" in rv.data, msg=rv.data)

    def test_global_toggle(self):
        with app.test_request_context():
            event = basic_setup(self.super_admin)
            url = url_for('settings.email_toggle_view')
            for value in [0, 1]:
                data = {
                    'name': 'global_email',
                    'value': value
                }

                rv = self.app.post(url, follow_redirects=True, buffered=True, data=data)
                result = json.loads(rv.data)
                for notification_setting_id in result[u'notification_setting_ids']:
                    notification = DataGetter.get_email_notification_settings_by_id(notification_setting_id)
                    asset_notification(self, notification, data['value'])

    def test_individual_toggle(self):
        with app.test_request_context():
            event = basic_setup(self.super_admin)
            for value in [0, 1]:
                data = {
                    'value': value,
                    'event_id': event.id
                }
                url = url_for('settings.email_toggle_view')
                for field in email_fields:
                    data['name'] = field
                    rv = self.app.post(url, follow_redirects=True, buffered=True, data=data)
                    result = json.loads(rv.data)
                    for notification_setting_id in result[u'notification_setting_ids']:
                        notification = DataGetter.get_email_notification_settings_by_id(notification_setting_id)
                        self.assertEqual(getattr(notification, field), data['value'])

if __name__ == '__main__':
    unittest.main()

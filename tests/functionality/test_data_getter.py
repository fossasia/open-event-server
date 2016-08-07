"""Copyright 2016 Rafal Kowalski"""
import unittest
from tests.utils import OpenEventTestCase


from app import current_app as app
from app.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from app.helpers.data_getter import DataGetter


class TestDataGetter(OpenEventTestCase):

    def test_all_user_notifications(self):
        with app.test_request_context():
            user = ObjectMother.get_user()
            self.assertEquals(DataGetter().get_all_user_notifications(user), [])

    def test_get_user_notification(self):
        with app.test_request_context():
            notification = ObjectMother.get_notification()
            save_to_db(notification, 'Save')
            self.assertTrue(DataGetter.get_user_notification(1))

    # def test_latest_notif(self):
    #     with app.test_request_context():
    #         user = ObjectMother.get_user()
    #         notification = DataGetter.get_latest_notif(user)
    #         self.assertTrue(notification)

    def test_get_invite_by_user(self):
        with app.test_request_context():
            notification = ObjectMother.get_notification()
            save_to_db(notification, 'Save')
            invite = DataGetter.get_invite_by_user_id(1)
            self.assertFalse(invite)

    def test_all_events(self):
        with app.test_request_context():
            self.assertEquals(DataGetter().get_all_events(), [])

    def test_get_all_users_events_roles(self):
        with app.test_request_context():
            self.assertTrue(DataGetter.get_all_users_events_roles())

    def test_get_event_roles_for_user(self):
        with app.test_request_context():
            user = ObjectMother.get_user()
            save_to_db(user)
            self.assertTrue(DataGetter.get_event_roles_for_user(user.id))

    def test_get_roles(self):
        with app.test_request_context():
            self.assertTrue(DataGetter.get_roles())

    def test_get_roles_by_name(self):
        with app.test_request_context():
            self.assertTrue(DataGetter.get_role_by_name('organizer'))

    def test_get_services(self):
        with app.test_request_context():
            self.assertTrue(DataGetter.get_services())

    def test_get_all_events_owners(self):
        with app.test_request_context():
            self.assertEquals(DataGetter.get_all_owner_events())
if __name__ == '__main__':
    unittest.main()

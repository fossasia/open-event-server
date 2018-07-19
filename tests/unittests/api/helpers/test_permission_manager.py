import unittest

from flask import Response
from flask_jwt import _default_jwt_encode_handler

from app import current_app as app
from app.api.helpers.db import get_or_create, save_to_db
from app.api.helpers.permission_manager import has_access, accessible_role_based_events, permission_manager
from app.factories.event import EventFactoryBasic
from app.models.users_events_role import UsersEventsRoles
from tests.unittests.utils import OpenEventTestCase
from app.factories.user import UserFactory
from app.models import db
from tests.unittests.setup_database import Setup


class TestPermissionManager(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            user = UserFactory()
            db.session.add(user)
            db.session.commit()

            event = EventFactoryBasic()
            event.user_id = user.id
            db.session.add(event)
            db.session.commit()

            # Authenticate User
            self.auth = {'Authorization': "JWT " + str(_default_jwt_encode_handler(user), 'utf-8')}

    def test_has_access(self):
        with app.test_request_context(headers=self.auth):
            self.assertTrue(has_access('is_admin'))
            self.assertFalse(has_access('is_super_admin'))
            self.assertTrue(has_access('is_organizer', event_id=1))

    def test_accessible_role_based_events(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            response = accessible_role_based_events(lambda *a, **b: b.get('user_id'), (), {}, (), {})
            assert response is not None

    def test_is_organizer(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 1
            save_to_db(uer)
            self.assertTrue(has_access('is_organizer', event_id=1))

    def test_is_coorganizer(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 2
            save_to_db(uer)
            self.assertTrue(has_access('is_coorganizer', event_id=1))

    def test_is_coorganizer_endpoint_related_to_event(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 2
            save_to_db(uer)
            self.assertTrue(has_access('is_coorganizer', event_id=1))

    def test_is_moderator(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 4
            save_to_db(uer)
            self.assertTrue(has_access('is_moderator', event_id=1))

    def test_is_track_organizer(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 4
            save_to_db(uer)
            self.assertTrue(has_access('is_moderator', event_id=1))

    def test_is_registrar(self):
        with app.test_request_context(headers=self.auth, method="POST"):
            uer, is_created = get_or_create(UsersEventsRoles, user_id=1, event_id=1)
            uer.role_id = 6
            save_to_db(uer)
            self.assertTrue(has_access('is_registrar', event_id=1))

    def test_permission_manager_attributes(self):
        with app.test_request_context():
            kwargs = {'leave_if': lambda a: True}
            perm = permission_manager(lambda *a, **b: True, [], {}, 'is_admin', **kwargs)
            self.assertTrue(perm)

            kwargs = {'check': lambda a: False}
            perm = permission_manager(lambda *a, **b: False, [], {}, 'is_admin', **kwargs)
            self.assertIsInstance(perm, Response)


if __name__ == '__main__':
    unittest.main()

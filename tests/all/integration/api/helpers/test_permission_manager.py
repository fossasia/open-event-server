import unittest

from flask_jwt_extended import create_access_token

from app.api.helpers.db import save_to_db
from app.api.helpers.errors import ForbiddenError
from app.api.helpers.permission_manager import (
    accessible_role_based_events,
    has_access,
    permission_manager,
)
from tests.all.integration.utils import OpenEventLegacyTestCase
from tests.factories.event import EventFactoryBasic
from tests.factories.user import UserFactory
from tests.factories.users_events_roles import UsersEventsRolesSubFactory
import pytest


class TestPermissionManager(OpenEventLegacyTestCase):
    def setUp(self):
        super().setUp()
        with self.app.test_request_context():
            user = UserFactory()
            save_to_db(user)

            event = EventFactoryBasic()
            event.user_id = user.id
            save_to_db(event)

            # Authenticate User
            self.auth = {
                'Authorization': "JWT " + create_access_token(user.id, fresh=True)
            }

    def test_has_access(self):
        """Method to test whether user has access to different roles"""

        with self.app.test_request_context(headers=self.auth):
            assert has_access('is_admin')
            assert not has_access('is_super_admin')
            assert has_access('is_organizer', event_id=1)

    def test_accessible_role_based_events(self):
        """Method to test accessible role of a user based on an event"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            response = accessible_role_based_events(
                lambda *a, **b: b.get('user_id'), (), {}, (), {}
            )
            assert response is not None

    def test_is_organizer(self):
        """Method to test whether a user is organizer of an event or not"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            uer = UsersEventsRolesSubFactory(
                user_id=1, event_id=1, role__name='organizer'
            )
            save_to_db(uer)
            assert has_access('is_organizer', event_id=1)

    def test_is_coorganizer(self):
        """Method to test whether a user is coorganizer of an event or not"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            uer = UsersEventsRolesSubFactory(
                user_id=1, event_id=1, role__name='coorganizer'
            )
            save_to_db(uer)
            assert has_access('is_coorganizer', event_id=1)

    def test_is_moderator(self):
        """Method to test whether a user is moderator of an event or not"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            uer = UsersEventsRolesSubFactory(
                user_id=1, event_id=1, role__name='moderator'
            )
            save_to_db(uer)
            assert has_access('is_moderator', event_id=1)

    def test_is_track_organizer(self):
        """Method to test whether a user is track organizer of an event or not"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            uer = UsersEventsRolesSubFactory(
                user_id=1, event_id=1, role__name='track_organizer'
            )
            save_to_db(uer)
            assert has_access('is_track_organizer', event_id=1)

    def test_is_registrar(self):
        """Method to test whether a user is registrar of an event or not"""

        with self.app.test_request_context(headers=self.auth, method="POST"):
            uer = UsersEventsRolesSubFactory(
                user_id=1, event_id=1, role__name='registrar'
            )
            save_to_db(uer)
            assert has_access('is_registrar', event_id=1)

    def test_permission_manager_attributes(self):
        """Method to test attributes of permission manager"""

        with self.app.test_request_context():
            kwargs = {'leave_if': lambda a: True}
            perm = permission_manager(lambda *a, **b: True, [], {}, 'is_admin', **kwargs)
            assert perm

            kwargs = {'check': lambda a: False}
            with pytest.raises(ForbiddenError):
                permission_manager(lambda *a, **b: False, [], {}, 'is_admin', **kwargs)


if __name__ == '__main__':
    unittest.main()

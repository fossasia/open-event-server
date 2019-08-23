import unittest

from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app import current_app as app
from app.models import db
from app.api.helpers.db import save_to_db
from app.models.users_events_role import UsersEventsRoles
from app.api.helpers.role_invite import delete_previous_uer
from app.factories.user_event_role import UsersEventsRoleFactory


class TestRoleInvite(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_user_role_event_delete(self):
        """Test to check deletion of previous owners for role invites"""

        with app.test_request_context():
            uer = UsersEventsRoleFactory()
            save_to_db(uer)
            delete_previous_uer(uer)
            uer_entry = db.session.query(UsersEventsRoles).filter_by(id=uer.id).first()
            self.assertEqual(None, uer_entry)


if __name__ == '__main__':
    unittest.main()

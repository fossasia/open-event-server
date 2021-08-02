from app.models.role import Role
import unittest
from unittest import TestCase

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.role_invites import RoleInviteSchema


class TestRoleInviteSchema(TestCase):
    def test_validate_status_pass(self):
        """
        Role Invite Validate Status - Tests if the function runs without an exception
        :return:
        """
        schema = RoleInviteSchema()
        data = {'role': '1', 'role_name': 'owner'}
        original_data = {'id': '1'}
        RoleInviteSchema.validate_satus(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

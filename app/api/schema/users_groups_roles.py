from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize


class UsersGroupsRolesSchema(Schema):
    """
    Api schema for users_grouops_role Model
    """

    class Meta:
        """
        Meta class for users_groups_role Api Schema
        """

        type_ = 'users-groups-roles'
        self_view = 'v1.users_groups_roles_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)

    group = Relationship(
        self_view='v1.users_groups_roles_group',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'users_groups_roles_id': '<id>'},
        schema='GroupSchema',
        type_='group',
    )

    user = Relationship(
        self_view='v1.users_groups_roles_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'users_events_roles_id': '<id>'},
        schema='UserSchemaPublic',
        type_="user",
    )

    role = Relationship(
        self_view='v1.users_groups_roles_role',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.role_detail',
        related_view_kwargs={'users_groups_roles_id': '<id>'},
        schema='RoleSchema',
        type_="role",
    )

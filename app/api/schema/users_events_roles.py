from marshmallow_jsonapi import Schema, fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize


class UsersEventsRolesSchema(Schema):
    """
    Api schema for users_events_role Model
    """

    class Meta:
        """
        Meta class for users_events_role Api Schema
        """

        type_ = 'users-events-roles'
        self_view = 'v1.users_events_roles_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)

    event = Relationship(
        self_view='v1.users_events_roles_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'users_events_roles_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

    user = Relationship(
        self_view='v1.users_events_roles_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'users_events_roles_id': '<id>'},
        schema='UserSchemaPublic',
        type_="user",
    )

    role = Relationship(
        self_view='v1.users_events_roles_role',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.role_detail',
        related_view_kwargs={'users_events_roles_id': '<id>'},
        schema='RoleSchema',
        type_="role",
    )

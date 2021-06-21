from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class GroupSchema(SoftDeletionSchema):
    """
    Api Schema for event type model
    """

    class Meta:
        """
        Meta class for event type Api Schema
        """

        type_ = 'group'
        self_view = 'v1.group_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    created_at = fields.DateTime(dump_only=True, timezone=True)

    events = Relationship(
        self_view='v1.group_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        related_view_kwargs={'group_id': '<id>'},
        many=True,
        schema='EventSchemaPublic',
        type_='event',
    )

    user = Relationship(
        attribute='user',
        self_view='v1.group_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'group_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
        dump_only=True,
    )

    roles = Relationship(
        self_view='v1.event_users_groups_roles',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.users_groups_roles_list',
        related_view_kwargs={'group_id': '<id>'},
        schema='UsersGroupsRolesSchema',
        type_='users-groups-role',
        many=True,
    )

    follower = Relationship(
        self_view='v1.group_followers',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_follow_group_list',
        related_view_kwargs={'group_id': '<id>'},
        schema='UserFollowGroupSchema',
        type_='user-follow-group',
    )

    followers = Relationship(
        self_view='v1.group_followers',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_follow_group_list',
        related_view_kwargs={'group_id': '<id>'},
        schema='UserFollowGroupSchema',
        many=True,
        type_='user-follow-group',
    )

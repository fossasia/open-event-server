from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from marshmallow_jsonapi.flask import Schema as JSONAPISchema

from app.api.helpers.utilities import dasherize


class UserFollowGroupSchema(JSONAPISchema):
    """
    Api schema for User Follow Group
    """

    class Meta:
        type_ = 'user-follow-group'
        self_view = 'v1.user_follow_group_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    created_at = fields.DateTime(dump_only=True, timezone=True)

    group = Relationship(
        attribute='group',
        self_view='v1.user_follow_group_group',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.group_detail',
        related_view_kwargs={'user_follow_group_id': '<id>'},
        schema='GroupSchema',
        type_='group',
    )

    user = Relationship(
        attribute='user',
        self_view='v1.user_follow_group_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'user_follow_group_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class GroupFollowerSchema(Schema):
    """
    Api schema for Group Follower Model
    """

    class Meta:
        type_ = 'user-group-followed'
        self_view = 'v1.user_group_followed_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)

    group = Relationship(
        attribute='group',
        self_view='v1.user_followed_group_group',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.group_detail',
        related_view_kwargs={'user_followed_group_id': '<id>'},
        schema='GroupSchema',
        type_='group',
    )

    user = Relationship(
        attribute='user',
        self_view='v1.user_followed_group_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'user_followed_group_id': '<id>'},
        schema='UserSchema',
        type_='user',
    )

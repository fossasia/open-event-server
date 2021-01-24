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

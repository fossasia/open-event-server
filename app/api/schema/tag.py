from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class TagSchema(SoftDeletionSchema):
    """API Schema for user tag Model"""

    class Meta:
        """Meta class for user tag API schema"""

        type_ = 'tag'
        self_view = 'v1.tags_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    color = fields.Str(allow_none=True)
    is_read_only = fields.Boolean(required=False)
    event = Relationship(
        self_view='v1.tags_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'tag_id': '<id>'},
        schema='EventSchema',
        type_='event',
    )

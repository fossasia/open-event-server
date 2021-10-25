from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class EventLocationSchema(Schema):
    """
    Api Schema for event location model
    """

    class Meta:
        """
        Meta class for event type Api Schema
        """

        type_ = 'event-location'
        inflect = dasherize

    id = fields.Str()
    name = fields.Str(required=True)
    slug = fields.Str(dump_only=True)
    events = Relationship(
        related_view='v1.event_list',
        related_view_kwargs={'event_location_id': '<id>'},
        many=True,
        schema='EventSchemaPublic',
        type_='event',
    )

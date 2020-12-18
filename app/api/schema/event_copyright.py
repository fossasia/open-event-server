from datetime import datetime

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class EventCopyrightSchema(SoftDeletionSchema):
    class Meta:
        type_ = 'event-copyright'
        self_view = 'v1.event_copyright_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    holder = fields.Str(allow_none=True)
    holder_url = fields.Url(allow_none=True)
    licence = fields.Str(required=True)
    licence_url = fields.Url(allow_none=True)
    year = fields.Int(
        validate=lambda n: 1900 <= n <= datetime.now().year, allow_none=True
    )
    logo_url = fields.Url(attribute='logo', allow_none=True)
    event = Relationship(
        self_view='v1.copyright_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'copyright_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

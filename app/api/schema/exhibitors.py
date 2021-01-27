from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize


class ExhibitorSchema(Schema):
    class Meta:

        type_ = 'exhibitor'
        self_view = 'v1.exhibitor_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    url = fields.Url(allow_none=True)
    position = fields.Integer(allow_none=True, default=0)
    logo_url = fields.Url(allow_none=True)
    banner_url = fields.Url(allow_none=True)
    video_url = fields.Url(allow_none=True)
    slides_url = fields.Url(allow_none=True)
    event = Relationship(
        related_view='v1.event_detail',
        related_view_kwargs={'exhibitor_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class MicrolocationSchema(SoftDeletionSchema):
    """
    Api schema for Microlocation Model
    """

    class Meta:
        """
        Meta class for Microlocation Api Schema
        """
        type_ = 'microlocation'
        self_view = 'v1.microlocation_detail'
        self_view_kwargs = {'id': '<id>'}
        self_view_many = 'v1.microlocation_list_post'
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    latitude = fields.Float(validate=lambda n: -90 <= n <= 90, allow_none=True)
    longitude = fields.Float(validate=lambda n: -180 <= n <= 180, allow_none=True)
    floor = fields.Integer(allow_none=True)
    room = fields.Str(allow_none=True)
    sessions = Relationship(attribute='session',
                            many=True,
                            self_view='v1.microlocation_session',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'microlocation_id': '<id>'},
                            schema='SessionSchema',
                            type_='session')
    event = Relationship(attribute='event',
                         self_view='v1.microlocation_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'microlocation_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

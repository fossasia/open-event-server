from datetime import datetime

from marshmallow import validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class SessionTypeSchema(SoftDeletionSchema):
    """
    Api Schema for session type model
    """

    class Meta:
        """
        Meta class for SessionTypeSchema
        """

        type_ = 'session-type'
        self_view = 'v1.session_type_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema
    def validate_length(self, data):
        if 'length' not in data:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/length'},
                "Length attribute is missing",
            )
        try:
            datetime.strptime(data['length'], '%H:%M')
        except ValueError:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/length'},
                "Length should be in the format %H:%M",
            )

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    length = fields.Str(required=True)
    position = fields.Integer(allow_none=True, default=0)
    event = Relationship(
        self_view='v1.session_type_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'session_type_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    sessions = Relationship(
        self_view='v1.session_type_sessions',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.session_list',
        related_view_kwargs={'session_type_id': '<id>'},
        schema='SessionSchema',
        many=True,
        type_='session',
    )

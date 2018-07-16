import re

from marshmallow import validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class TrackSchema(SoftDeletionSchema):
    """
    Api Schema for track model
    """

    class Meta:
        """
        Meta class for User Api Schema
        """
        type_ = 'track'
        self_view = 'v1.track_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema
    def valid_color(self, data):
        if not re.search(r'^#(?:[0-9a-fA-F]{3}){1,2}$', data['color']):
            return UnprocessableEntity({'pointer': 'data/attributes/color'}, "Color should be proper HEX color code")

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    color = fields.Str(required=True)
    font_color = fields.Str(allow_none=True, dump_only=True)
    event = Relationship(attribute='event',
                         self_view='v1.track_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'track_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    sessions = Relationship(attribute='sessions',
                            self_view='v1.track_sessions',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.session_list',
                            related_view_kwargs={'track_id': '<id>'},
                            schema='SessionSchema',
                            many=True,
                            type_='session')

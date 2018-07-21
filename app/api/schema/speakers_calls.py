from marshmallow import validates_schema, validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.speakers_call import SpeakersCall


class SpeakersCallSchema(SoftDeletionSchema):
    """
    Api Schema for Speakers Call model
    """
    class Meta:
        """
        Meta class for Speakers Call Api Schema
        """
        type_ = 'speakers-call'
        self_view = 'v1.speakers_call_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            speakers_calls = SpeakersCall.query.filter_by(id=original_data['data']['id']).one()

            if 'starts_at' not in data:
                data['starts_at'] = speakers_calls.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = speakers_calls.ends_at

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/ends-at'}, "ends-at should be after starts-at")

    id = fields.Str(dump_only=True)
    announcement = fields.Str(required=True)
    starts_at = fields.DateTime(required=True)
    ends_at = fields.DateTime(required=True)
    hash = fields.Str(allow_none=True)
    privacy = fields.String(validate=validate.OneOf(choices=["private", "public"]), allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.speakers_call_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'speakers_call_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

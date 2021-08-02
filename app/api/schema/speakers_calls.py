from marshmallow import validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.errors import UnprocessableEntityError
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
            speakers_calls = SpeakersCall.query.filter_by(
                id=original_data['data']['id']
            ).one()

            if 'starts_at' not in data:
                data['starts_at'] = speakers_calls.starts_at

            if 'ends_at' not in data:
                data['ends_at'] = speakers_calls.ends_at

            # if 'event_starts_at' not in data:
            #     data['event_starts_at'] = speakers_calls.event.starts_at

        if data['starts_at'] >= data['ends_at']:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/ends-at'},
                "ends-at should be after starts-at",
            )

        # if 'event_starts_at' in data and data['starts_at'] > data['event_starts_at']:
        #     raise UnprocessableEntityError({'pointer': '/data/attributes/starts-at'},
        #                               "speakers-call starts-at should be before event starts-at")

        # if 'event_starts_at' in data and data['ends_at'] > data['event_starts_at']:
        #     raise UnprocessableEntityError({'pointer': '/data/attributes/ends-at'},
        #                               "speakers-call ends-at should be before event starts-at")

    id = fields.Str(dump_only=True)
    announcement = fields.Str(allow_none=True)
    starts_at = fields.DateTime(required=True)
    soft_ends_at = fields.DateTime(allow_none=True)
    ends_at = fields.DateTime(required=True)
    hash = fields.Str(allow_none=True)
    privacy = fields.String(
        validate=validate.OneOf(choices=["private", "public"]), allow_none=True
    )
    event = Relationship(
        self_view='v1.speakers_call_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'speakers_call_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

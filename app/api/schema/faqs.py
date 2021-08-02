from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema


class FaqSchema(SoftDeletionSchema):
    """
    Api schema for page Model
    """

    class Meta:
        """
        Meta class for page Api Schema
        """

        type_ = 'faq'
        self_view = 'v1.faq_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    question = fields.Str(required=True)
    answer = fields.Str(required=True)
    event = Relationship(
        self_view='v1.faq_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'faq_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    faq_type = Relationship(
        self_view='v1.faq_faq_type',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.faq_type_detail',
        related_view_kwargs={'faq_id': '<id>'},
        schema='FaqTypeSchemaPublic',
        type_='faq-type',
    )

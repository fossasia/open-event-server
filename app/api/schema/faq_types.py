from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.utilities import dasherize


class FaqTypeSchema(Schema):
    """
    Api Schema for faq type model
    """

    class Meta:
        """
        Meta class for FaqTypeSchema
        """
        type_ = 'faq-type'
        self_view = 'v1.faq_type_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    event = Relationship(attribute='event',
                         self_view='v1.faq_type_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'faq_type_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    faqs = Relationship(attribute='faqs',
                        self_view='v1.faq_type_faqs',
                        self_view_kwargs={'id': '<id>'},
                        related_view='v1.faq_list',
                        related_view_kwargs={'faq_type_id': '<id>'},
                        schema='FaqSchema',
                        many=True,
                        type_='faq')

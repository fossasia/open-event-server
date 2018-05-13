from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.utilities import dasherize
from utils.common import use_defaults


@use_defaults()
class TaxSchemaPublic(Schema):
    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    rate = fields.Float(validate=lambda n: 0 <= n <= 100, required=True)
    is_tax_included_in_price = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.tax_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'tax_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')


class TaxSchema(Schema):
    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    country = fields.Str(allow_none=True)
    name = fields.Str(required=True)
    rate = fields.Float(validate=lambda n: 0 <= n <= 100, required=True)
    tax_id = fields.Str(required=True)
    should_send_invoice = fields.Boolean(default=False)
    registered_company = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    zip = fields.Integer(allow_none=True)
    invoice_footer = fields.Str(allow_none=True)
    is_tax_included_in_price = fields.Boolean(default=False)
    event = Relationship(attribute='event',
                         self_view='v1.tax_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'tax_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

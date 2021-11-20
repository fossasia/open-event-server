from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class TaxSchemaPublic(SoftDeletionSchema):
    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(allow_none=True, default='')
    rate = fields.Float(validate=lambda n: 0 <= n <= 100, allow_none=True, default=0)
    is_tax_included_in_price = fields.Boolean(default=False)
    event = Relationship(
        self_view='v1.tax_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'tax_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )


class TaxSchema(TaxSchemaPublic):
    class Meta:
        type_ = 'tax'
        self_view = 'v1.tax_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    country = fields.Str(allow_none=True)
    tax_id = fields.Str(allow_none=True, default='')
    should_send_invoice = fields.Boolean(default=False)
    is_invoice_sent = fields.Boolean(default=False)
    registered_company = fields.Str(allow_none=True)
    contact_name = fields.Str(allow_none=True)
    phone = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    zip = fields.Str(allow_none=True)
    invoice_footer = fields.Str(allow_none=True)

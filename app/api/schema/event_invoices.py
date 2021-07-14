from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from utils.common import use_defaults


@use_defaults()
class EventInvoiceSchema(SoftDeletionSchema):
    """
    Event Invoice API Schema based on event invoice model
    """

    class Meta:
        type_ = 'event-invoice'
        self_view = 'v1.event_invoice_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    identifier = fields.Str(allow_none=True)
    amount = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    created_at = fields.DateTime(allow_none=True)
    issued_at = fields.DateTime(dump_only=True)
    due_at = fields.DateTime(dump_only=True)
    completed_at = fields.DateTime(default=None, allow_none=True)
    transaction_id = fields.Str(allow_none=True)
    paid_via = fields.Str(
        validate=validate.OneOf(
            choices=["free", "stripe", "paypal", "transfer", "onsite", "cheque"]
        ),
        allow_none=True,
    )
    payment_mode = fields.Str(allow_none=True)
    brand = fields.Str(allow_none=True)
    exp_month = fields.Integer(validate=lambda n: 0 <= n <= 12, allow_none=True)
    exp_year = fields.Integer(validate=lambda n: n >= 2015, allow_none=True)
    last4 = fields.Str(allow_none=True)
    stripe_token = fields.Str(allow_none=True)
    paypal_token = fields.Str(allow_none=True)
    status = fields.Str(
        validate=validate.OneOf(
            choices=["paid", "due", "refunding", "refunded", "failed", "resolved"]
        ),
        allow_none=True,
    )
    invoice_pdf_url = fields.Url(allow_none=True)
    user = Relationship(
        self_view='v1.event_invoice_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'event_invoice_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
    )
    event = Relationship(
        self_view='v1.event_invoice_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'event_invoice_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

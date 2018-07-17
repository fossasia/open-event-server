from marshmallow import validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.helpers.static import PAYMENT_CURRENCY_CHOICES
from app.api.helpers.utilities import dasherize


class TicketFeesSchema(Schema):
    """
    Api schema for ticket_fee Model
    """
    class Meta:
        """
        Meta class for image_size Api Schema
        """
        type_ = 'ticket-fee'
        self_view = 'v1.ticket_fee_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer(dump_only=True)
    currency = fields.Str(validate=validate.OneOf(choices=PAYMENT_CURRENCY_CHOICES), allow_none=True)
    country = fields.String(allow_none=True)
    service_fee = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    maximum_fee = fields.Float(validate=lambda n: n >= 0, allow_none=True)

from flask import request
from marshmallow import post_dump, validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship, Schema

from app.api.helpers.utilities import dasherize
from app.api.schema.base import GetterRelationship
from app.models import db
from utils.common import use_defaults


class OnSiteTicketSchema(Schema):
    class Meta:
        type_ = 'on-site-ticket'
        inflect = dasherize

    id = fields.Str(load_only=True, required=True)
    quantity = fields.Str(load_only=True, required=True)


@use_defaults()
class OrderSchema(Schema):
    class Meta:
        type_ = 'order'
        self_view = 'v1.order_detail'
        self_view_kwargs = {'order_identifier': '<identifier>'}
        inflect = dasherize

    @post_dump
    def generate_payment_url(self, data):
        """
        generate payment url for an order
        :param data:
        :return:
        """
        if (
            'POST' in request.method
            or ('GET' in request.method and 'regenerate' in request.args)
            and data["status"] != 'completed'
        ):
            if data['payment_mode'] == 'stripe':
                data['payment_url'] = 'stripe://payment'
        return data

    @validates_schema
    def initial_values(self, data):
        if data.get('payment_mode') is None and 'POST' in request.method:
            data['payment_mode'] = 'free'
        return data

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    amount = fields.Float(validate=lambda n: n >= 0, allow_none=False, default=0)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(db.String, allow_none=True)
    country = fields.Str(allow_none=True)
    zipcode = fields.Str(allow_none=True)
    company = fields.Str(allow_none=True)
    tax_business_info = fields.Str(allow_none=True)
    completed_at = fields.DateTime(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    transaction_id = fields.Str(dump_only=True)
    payment_mode = fields.Str(
        default="free",
        validate=validate.OneOf(
            choices=[
                "free",
                "stripe",
                "paypal",
                "bank",
                "cheque",
                "onsite",
                "omise",
                "alipay",
                "paytm",
                "invoice"
            ]
        ),
        allow_none=True,
    )
    paid_via = fields.Str(dump_only=True)
    is_billing_enabled = fields.Boolean(default=False)
    brand = fields.Str(dump_only=True)
    exp_month = fields.Str(dump_only=True)
    exp_year = fields.Str(dump_only=True)
    last4 = fields.Str(dump_only=True)
    status = fields.Str(
        validate=validate.OneOf(
            choices=[
                "initializing",
                "pending",
                "cancelled",
                "completed",
                "placed",
                "expired",
            ]
        )
    )
    discount_code_id = fields.Str(allow_none=True)
    payment_url = fields.Str(dump_only=True)
    cancel_note = fields.Str(allow_none=True)
    order_notes = fields.Str(allow_none=True)
    tickets_pdf_url = fields.Url(dump_only=True)

    # only used in the case of an on site attendee.
    on_site_tickets = fields.List(
        cls_or_instance=fields.Nested(OnSiteTicketSchema), load_only=True, allow_none=True
    )

    attendees = GetterRelationship(
        getter='filtered_ticket_holders',
        attribute='ticket_holders',
        self_view='v1.order_attendee',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.attendee_list',
        related_view_kwargs={'order_identifier': '<identifier>'},
        schema='AttendeeSchemaPublic',
        many=True,
        type_='attendee',
        dump_only=True,
    )

    tickets = Relationship(
        self_view='v1.order_ticket',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.ticket_list',
        related_view_kwargs={'order_identifier': '<identifier>'},
        schema='TicketSchemaPublic',
        many=True,
        type_="ticket",
        dump_only=True,
    )

    user = GetterRelationship(
        getter='safe_user',
        self_view='v1.order_user',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.user_detail',
        related_view_kwargs={'id': '<user_id>'},
        schema='UserSchemaPublic',
        type_="user",
        dump_only=True,
    )

    event = Relationship(
        self_view='v1.order_event',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.event_detail',
        related_view_kwargs={'id': '<event_id>'},
        schema='EventSchemaPublic',
        type_="event",
        dump_only=True,
    )

    event_invoice = Relationship(
        attribute='invoice',
        self_view='v1.order_event_invoice',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.event_invoice_detail',
        related_view_kwargs={'id': '<id>'},
        schema='EventInvoiceSchema',
        type_="event_invoice",
        dump_only=True,
    )

    marketer = Relationship(
        self_view='v1.order_marketer',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.user_detail',
        related_view_kwargs={'id': '<marketer_id>'},
        schema='UserSchemaPublic',
        type_="user",
        dump_only=True,
    )

    discount_code = Relationship(
        self_view='v1.order_discount',
        self_view_kwargs={'order_identifier': '<identifier>'},
        related_view='v1.discount_code_detail',
        related_view_kwargs={'id': '<discount_code_id>'},
        schema='DiscountCodeSchemaPublic',
        type_="discount-code",
        dump_only=True,
    )

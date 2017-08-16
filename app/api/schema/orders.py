from flask import request
from marshmallow import post_dump, validates_schema, validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app import db
from app.api.helpers.payment import PayPalPaymentsManager
from app.api.helpers.utilities import dasherize
from app.models.order import Order


class OrderSchema(Schema):
    class Meta:
        type_ = 'order'
        self_view = 'v1.order_detail'
        self_view_kwargs = {'order_identifier': '<identifier>'}
        inflect = dasherize

    @post_dump
    def generate_payment_url(self, data):
        if 'POST' in request.method or ('GET' in request.method and 'regenerate' in request.args) and 'completed' != \
           data["status"]:
            if data['payment_mode'] == 'stripe':
                data['payment_url'] = 'stripe://payment'
            elif data['payment_mode'] == 'paypal':
                order = Order.query.filter_by(id=data['id']).first()
                data['payment_url'] = PayPalPaymentsManager.get_checkout_url(order)
        return data

    @validates_schema
    def initial_values(self, data):
        if data.get('payment_mode') is None and 'POST' in request.method:
            data['payment_mode'] = 'free'
        return data

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    amount = fields.Float(validate=lambda n: n > 0)
    address = fields.Str()
    city = fields.Str()
    state = fields.Str(db.String)
    country = fields.Str(required=True)
    zipcode = fields.Str()
    completed_at = fields.DateTime(dump_only=True)
    transaction_id = fields.Str(dump_only=True)
    payment_mode = fields.Str(default="free", required=True)
    paid_via = fields.Str(dump_only=True)
    brand = fields.Str(dump_only=True)
    exp_month = fields.Str(dump_only=True)
    exp_year = fields.Str(dump_only=True)
    last4 = fields.Str(dump_only=True)
    status = fields.Str(validate=validate.OneOf(choices=["pending", "cancelled", "confirmed", "deleted"]))
    discount_code_id = fields.Str()
    payment_url = fields.Str(dump_only=True)

    attendees = Relationship(attribute='ticket_holders',
                             self_view='v1.order_attendee',
                             self_view_kwargs={'order_identifier': '<identifier>'},
                             related_view='v1.attendee_list',
                             related_view_kwargs={'order_identifier': '<identifier>'},
                             schema='AttendeeSchema',
                             many=True,
                             type_='attendee')

    tickets = Relationship(self_view='v1.order_ticket',
                           self_view_kwargs={'order_identifier': '<identifier>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'order_identifier': '<identifier>'},
                           schema='TicketSchema',
                           many=True,
                           type_="ticket")

    user = Relationship(self_view='v1.order_user',
                        self_view_kwargs={'order_identifier': '<identifier>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'id': '<user_id>'},
                        schema='UserSchemaPublic',
                        type_="user")

    event = Relationship(self_view='v1.order_event',
                         self_view_kwargs={'order_identifier': '<identifier>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'id': '<event_id>'},
                         schema='EventSchemaPublic',
                         type_="event")

    marketer = Relationship(self_view='v1.order_marketer',
                            self_view_kwargs={'order_identifier': '<identifier>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'id': '<marketer_id>'},
                            schema='UserSchemaPublic',
                            type_="user")

    discount_code = Relationship(self_view='v1.order_discount',
                                 self_view_kwargs={'order_identifier': '<identifier>'},
                                 related_view='v1.discount_code_detail',
                                 related_view_kwargs={'id': '<discount_code_id>'},
                                 schema='DiscountCodeSchemaPublic',
                                 type_="discount-code")

    event_invoice = Relationship(self_view='v1.order_event_invoice',
                                 self_view_kwargs={'order_identifier': '<identifier>'},
                                 related_view='v1.event_invoice_detail',
                                 related_view_kwargs={'id': '<event_invoice_id>'},
                                 schema='EventInvoiceSchema',
                                 type_="event-invoice")

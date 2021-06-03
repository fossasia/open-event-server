from marshmallow import validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.discount_code import DiscountCode
from app.models.ticket import Ticket
from utils.common import use_defaults


@use_defaults()
class TicketSchemaPublic(SoftDeletionSchema):
    class Meta:
        type_ = 'ticket'
        self_view = 'v1.ticket_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            ticket = Ticket.query.filter_by(id=original_data['data']['id']).one()

            if 'sales_starts_at' not in data:
                data['sales_starts_at'] = ticket.sales_starts_at

            if 'sales_ends_at' not in data:
                data['sales_ends_at'] = ticket.sales_ends_at

            # if 'event_ends_at' not in data:
            #     data['event_ends_at'] = ticket.event.ends_at

        if data['sales_starts_at'] >= data['sales_ends_at']:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/sales-ends-at'},
                "sales-ends-at should be after sales-starts-at",
            )

        # if 'event_ends_at' in data and data['sales_starts_at'] > data['event_ends_at']:
        #     raise UnprocessableEntityError({'pointer': '/data/attributes/sales-starts-at'},
        #                               "ticket sales-starts-at should be before event ends-at")

        # if 'event_ends_at' in data and data['sales_ends_at'] > data['event_ends_at']:
        #     raise UnprocessableEntityError({'pointer': '/data/attributes/sales-ends-at'},
        #                               "ticket sales-ends-at should be before event ends-at")

    @validates_schema
    def validate_quantity(self, data):
        if 'max_order' in data and 'min_order' in data:
            if data['max_order'] < data['min_order']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/max-order'},
                    "max-order should be greater than or equal to min-order",
                )

        if 'quantity' in data and 'min_order' in data:
            if data['quantity'] < data['min_order']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/quantity'},
                    "quantity should be greater than or equal to min-order",
                )

        if 'min_price' in data and 'max_price' in data and data['type'] == 'donation':
            if data['min_price'] > data['max_price']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/min-price'},
                    "minimum price should be lesser than or equal to maximum price",
                )

        if 'quantity' in data and 'max_order' in data:
            if data['quantity'] < data['max_order']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/quantity'},
                    "quantity should be greater than or equal to max-order",
                )

        if 'quantity' in data and data['quantity'] <= 0:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/quantity'},
                "quantity should be greater than 0",
            )

    @validates_schema
    def validate_price(self, data):
        if 'type' not in data:
            return
        if data['type'] == 'paid' and ('price' not in data or data['price'] <= 0):
            raise UnprocessableEntityError(
                {'pointer': 'data/attributes/price'},
                "paid ticket price should be greater than 0",
            )

    @validates_schema(pass_original=True)
    def validate_discount_code(self, data, original_data):
        if (
            'relationships' in original_data
            and 'discount-codes' in original_data['data']['relationships']
        ):
            discount_codes = original_data['data']['relationships']['discount-codes']
            for code in discount_codes['data']:
                try:
                    DiscountCode.query.filter_by(id=code['id']).one()
                except NoResultFound:
                    raise UnprocessableEntityError(
                        {'pointer': '/data/relationships/discount-codes'},
                        "Discount code does not exist",
                    )

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    type = fields.Str(required=True)
    price = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    min_price = fields.Float(validate=lambda n: n >= 0)
    max_price = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    is_description_visible = fields.Boolean(default=False)
    position = fields.Integer(allow_none=True)
    is_fee_absorbed = fields.Boolean()
    sales_starts_at = fields.DateTime(required=True)
    sales_ends_at = fields.DateTime(required=True)
    is_hidden = fields.Boolean(default=False)
    min_order = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_order = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    is_checkin_restricted = fields.Boolean(default=True)
    auto_checkin_enabled = fields.Boolean(default=False)
    event = Relationship(
        self_view='v1.ticket_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'ticket_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

    ticket_tags = Relationship(
        attribute='tags',
        self_view='v1.ticket_ticket_tag',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_tag_list',
        related_view_kwargs={'ticket_id': '<id>'},
        schema='TicketTagSchema',
        many=True,
        type_='ticket-tag',
    )

    discount_codes = Relationship(
        self_view='v1.ticket_discount_codes',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.discount_code_list',
        related_view_kwargs={'ticket_id': '<id>'},
        schema='DiscountCodeSchemaTicket',
        many=True,
        type_='discount-code',
    )


class TicketSchema(TicketSchemaPublic):
    class Meta:
        type_ = 'ticket'
        self_view = 'v1.ticket_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    access_codes = Relationship(
        self_view='v1.ticket_access_code',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.access_code_list',
        related_view_kwargs={'ticket_id': '<id>'},
        schema='AccessCodeSchema',
        many=True,
        type_='access-code',
    )
    attendees = Relationship(
        self_view='v1.ticket_attendees',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.attendee_list_post',
        related_view_kwargs={'ticket_id': '<id>'},
        schema='AttendeeSchema',
        many=True,
        type_='attendee',
    )

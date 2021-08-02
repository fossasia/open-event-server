from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validate, validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.discount_code import DiscountCode
from app.models.ticket import Ticket


class DiscountCodeSchemaPublic(SoftDeletionSchema):
    """
    API Schema for discount_code Model
    For endpoints which allow somebody other than co-organizer/admin to access the resource.
    """

    class Meta:
        type_ = 'discount-code'
        self_view = 'v1.discount_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Integer()
    code = fields.Str(required=True)
    discount_url = fields.Url(allow_none=True)
    value = fields.Float(required=True)
    type = fields.Str(
        validate=validate.OneOf(choices=["amount", "percent"]), required=True
    )
    is_active = fields.Boolean()
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(allow_none=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_till = fields.DateTime(allow_none=True)
    used_for = fields.Str(
        validate=validate.OneOf(choices=["event", "ticket"]), allow_none=False
    )
    created_at = fields.DateTime(allow_none=True)

    event = Relationship(
        self_view='v1.discount_code_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'discount_code_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )

    @classmethod
    def quantity_validation_helper(obj, data):
        min_quantity = data.get('min_quantity', None)
        max_quantity = data.get('max_quantity', None)
        if min_quantity is not None and max_quantity is not None:
            if min_quantity > max_quantity:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/min-quantity'},
                    "min-quantity cannot be more than max-quantity",
                )


class DiscountCodeSchemaEvent(DiscountCodeSchemaPublic):
    """
    API Schema for discount_code Model
    """

    class Meta:
        type_ = 'discount-code'
        self_view = 'v1.discount_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_quantity(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(
                    id=original_data['data']['id']
                ).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")
            if 'min_quantity' not in data:
                data['min_quantity'] = discount_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = discount_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = discount_code.tickets_number

        DiscountCodeSchemaEvent.quantity_validation_helper(data)

        if data.get('tickets_number') and data.get('max_quantity'):
            if (
                data['max_quantity'] >= 0
                and data['tickets_number'] < data['max_quantity']
            ):
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/tickets-number'},
                    "tickets-number should be greater than max-quantity",
                )

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        ends_at = data.get('valid_till', None)
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(
                    id=original_data['data']['id']
                ).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'valid_from' not in data:
                data['valid_from'] = discount_code.valid_from

            ends_at = data.get('valid_till') or discount_code.valid_expire_time

        if ends_at and data['valid_from'] > ends_at:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/valid-till'},
                "valid_till should be after valid_from",
            )

    events = Relationship(
        self_view='v1.discount_code_events',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_list',
        related_view_kwargs={'discount_code_id': '<id>'},
        schema='EventSchemaPublic',
        many=True,
        type_='event',
    )


class DiscountCodeSchemaTicket(DiscountCodeSchemaPublic):
    """
    API Schema for discount_code Model
    """

    class Meta:
        type_ = 'discount-code'
        self_view = 'v1.discount_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_quantity(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(
                    id=original_data['data']['id']
                ).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'min_quantity' not in data:
                data['min_quantity'] = discount_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = discount_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = discount_code.tickets_number

        DiscountCodeSchemaTicket.quantity_validation_helper(data)

        if data.get('tickets_number') and data.get('max_quantity'):
            if (
                data['max_quantity'] >= 0
                and data['tickets_number'] < data['max_quantity']
            ):
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/tickets-number'},
                    "tickets-number should be greater than max-quantity",
                )

    @validates_schema(pass_original=True)
    def validate_value(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(
                    id=original_data['data']['id']
                ).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'type' not in data:
                data['type'] = discount_code.type

            if 'value' not in data:
                data['value'] = discount_code.value

        if data['type'] == "percent":
            if 'tickets' in data:
                for ticket in data['tickets']:
                    ticket_object = Ticket.query.filter_by(id=ticket).one()
                    if ticket_object.event_id != int(data.get('event')):
                        raise UnprocessableEntityError(
                            {'pointer': '/data/attributes/tickets'},
                            "Tickets should be of same event as discount code",
                        )
                    if not ticket_object.price:
                        raise UnprocessableEntityError(
                            {'pointer': '/data/attributes/tickets'},
                            "discount code cannot be applied on free tickets",
                        )
            if data['value'] < 0 or data['value'] > 100:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/value'},
                    "discount percent must be within range of 0 and 100",
                )

        if data['type'] == "amount":
            if 'tickets' in data:
                for ticket in data['tickets']:
                    ticket_object = Ticket.query.filter_by(id=ticket).one()
                    if not ticket_object.price:
                        raise UnprocessableEntityError(
                            {'pointer': '/data/attributes/tickets'},
                            "discount code cannot be applied on free tickets",
                        )
                    if ticket_object.price < data['value']:
                        raise UnprocessableEntityError(
                            {'pointer': '/data/attributes/value'},
                            "discount amount cannot be more than ticket amount",
                        )
            if data['value'] < 0:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/value'},
                    "discount amount cannot be less than zero",
                )

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        ends_at = data.get('valid_till', None)
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(
                    id=original_data['data']['id']
                ).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'valid_from' not in data:
                data['valid_from'] = discount_code.valid_from

            ends_at = data.get('valid_till') or discount_code.valid_expire_time

        if ends_at and data['valid_from'] > ends_at:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/valid-till'},
                "valid_till should be after valid_from",
            )

    marketer = Relationship(
        self_view='v1.discount_code_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'discount_code_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
    )

    tickets = Relationship(
        self_view='v1.discount_code_tickets',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_list',
        related_view_kwargs={'discount_code_id': '<id>'},
        schema='TicketSchemaPublic',
        many=True,
        type_='ticket',
    )

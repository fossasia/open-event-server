from flask_rest_jsonapi.exceptions import ObjectNotFound
from marshmallow import validates_schema, validate
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.discount_code import DiscountCode


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
    type = fields.Str(validate=validate.OneOf(choices=["amount", "percent"]), required=True)
    is_active = fields.Boolean()
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    valid_from = fields.DateTime(allow_none=True)
    valid_till = fields.DateTime(allow_none=True)
    used_for = fields.Str(validate=validate.OneOf(choices=["event", "ticket"]), allow_none=False)
    created_at = fields.DateTime(allow_none=True)

    event = Relationship(attribute='event',
                         self_view='v1.discount_code_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'discount_code_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')

    @classmethod
    def quantity_validation_helper(obj, data):
        min_quantity = data.get('min_quantity', None)
        max_quantity = data.get('max_quantity', None)
        if min_quantity is not None and max_quantity is not None:
            if min_quantity > max_quantity:
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/min-quantity'},
                    "min-quantity cannot be more than max-quantity"
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
                discount_code = DiscountCode.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")
            if 'min_quantity' not in data:
                data['min_quantity'] = discount_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = discount_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = discount_code.tickets_number

        DiscountCodeSchemaEvent.quantity_validation_helper(data)

        if 'tickets_number' in data and 'max_quantity' in data:
            if data['tickets_number'] < data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/tickets-number'},
                                          "tickets-number should be greater than max-quantity")

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'valid_from' not in data:
                data['valid_from'] = discount_code.valid_from

            if 'valid_till' not in data:
                data['valid_till'] = discount_code.valid_till

        if data['valid_from'] >= data['valid_till']:
            raise UnprocessableEntity({'pointer': '/data/attributes/valid-till'},
                                      "valid_till should be after valid_from")

    events = Relationship(attribute='events',
                          self_view='v1.discount_code_events',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.event_list',
                          related_view_kwargs={'discount_code_id': '<id>'},
                          schema='EventSchemaPublic',
                          many=True,
                          type_='event')


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
                discount_code = DiscountCode.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'min_quantity' not in data:
                data['min_quantity'] = discount_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = discount_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = discount_code.tickets_number

        DiscountCodeSchemaTicket.quantity_validation_helper(data)

        if 'tickets_number' in data and 'max_quantity' in data:
            if data['tickets_number'] < data['max_quantity']:
                raise UnprocessableEntity({'pointer': '/data/attributes/tickets-number'},
                                          "tickets-number should be greater than max-quantity")

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        if 'id' in original_data['data']:
            try:
                discount_code = DiscountCode.query.filter_by(id=original_data['data']['id']).one()
            except NoResultFound:
                raise ObjectNotFound({'parameter': '{code}'}, "DiscountCode: not found")

            if 'valid_from' not in data:
                data['valid_from'] = discount_code.valid_from

            if 'valid_till' not in data:
                data['valid_till'] = discount_code.valid_till

        if data['valid_from'] >= data['valid_till']:
            raise UnprocessableEntity({'pointer': '/data/attributes/valid-till'},
                                      "valid_till should be after valid_from")

    marketer = Relationship(attribute='user',
                            self_view='v1.discount_code_user',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'discount_code_id': '<id>'},
                            schema='UserSchemaPublic',
                            type_='user')

    tickets = Relationship(attribute='tickets',
                           self_view='v1.discount_code_tickets',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'discount_code_id': '<id>'},
                           schema='TicketSchemaPublic',
                           many=True,
                           type_='ticket')

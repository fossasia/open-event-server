from marshmallow import validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Relationship

from app.api.helpers.errors import UnprocessableEntityError
from app.api.helpers.utilities import dasherize
from app.api.schema.base import SoftDeletionSchema
from app.models.access_code import AccessCode
from utils.common import use_defaults


@use_defaults()
class AccessCodeSchema(SoftDeletionSchema):
    """
    Api schema for Access Code Model
    """

    class Meta:
        """
        Meta class for Access Code Api Schema
        """

        type_ = 'access-code'
        self_view = 'v1.access_code_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @validates_schema(pass_original=True)
    def validate_date(self, data, original_data):
        ends_at = data.get('valid_till', None)
        if 'id' in original_data['data']:
            access_code = AccessCode.query.filter_by(id=original_data['data']['id']).one()

            if 'valid_from' not in data:
                data['valid_from'] = access_code.valid_from

            ends_at = data.get('valid_till') or access_code.valid_expire_time

        if ends_at and data['valid_from'] > ends_at:
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/valid-till'},
                "valid_till should be after valid_from",
            )

    @validates_schema(pass_original=True)
    def validate_order_quantity(self, data, original_data):
        if 'id' in original_data['data']:
            access_code = AccessCode.query.filter_by(id=original_data['data']['id']).one()

            if 'min_quantity' not in data:
                data['min_quantity'] = access_code.min_quantity

            if 'max_quantity' not in data:
                data['max_quantity'] = access_code.max_quantity

            if 'tickets_number' not in data:
                data['tickets_number'] = access_code.tickets_number

        min_quantity = data.get('min_quantity', None)
        max_quantity = data.get('max_quantity', None)
        tickets_number = data.get('tickets_number', None)
        if min_quantity and max_quantity and (min_quantity > max_quantity):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/min-quantity'},
                "min-quantity should be less than max-quantity",
            )

        if tickets_number and max_quantity and (tickets_number < max_quantity):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/tickets-number'},
                "tickets-number should be greater than max-quantity",
            )

    id = fields.Integer(dump_ony=True)
    code = fields.Str(required=True)
    access_url = fields.Url(allow_none=True)
    is_active = fields.Boolean(default=False)

    # For event level access this holds the max. uses
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)

    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    valid_from = fields.DateTime(required=True)
    valid_till = fields.DateTime(allow_none=True)
    event = Relationship(
        self_view='v1.access_code_event',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.event_detail',
        related_view_kwargs={'access_code_id': '<id>'},
        schema='EventSchemaPublic',
        type_='event',
    )
    marketer = Relationship(
        attribute='user',
        self_view='v1.access_code_user',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.user_detail',
        related_view_kwargs={'access_code_id': '<id>'},
        schema='UserSchemaPublic',
        type_='user',
    )
    tickets = Relationship(
        self_view='v1.access_code_tickets',
        self_view_kwargs={'id': '<id>'},
        related_view='v1.ticket_list',
        related_view_kwargs={'access_code_id': '<id>'},
        schema='TicketSchemaPublic',
        many=True,
        type_='ticket',
    )

from marshmallow import validates_schema
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship

from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import dasherize
from app.models.access_code import AccessCode


class AccessCodeSchema(Schema):
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
        if 'id' in original_data['data']:
            access_code = AccessCode.query.filter_by(id=original_data['data']['id']).one()

            if 'valid_from' not in data:
                data['valid_from'] = access_code.valid_from

            if 'valid_till' not in data:
                data['valid_till'] = access_code.valid_till

        if data['valid_from'] >= data['valid_till']:
            raise UnprocessableEntity({'pointer': '/data/attributes/valid-till'},
                                      "valid_till should be after valid_from")

    @validates_schema
    def validate_order_quantity(self, data):
        if 'max_order' in data and 'min_order' in data:
            if data['max_order'] < data['min_order']:
                raise UnprocessableEntity({'pointer': '/data/attributes/max-order'},
                                          "max-order should be greater than min-order")

        if 'quantity' in data and 'min_order' in data:
            if data['quantity'] < data['min_order']:
                raise UnprocessableEntity({'pointer': '/data/attributes/quantity'},
                                          "quantity should be greater than min-order")

    id = fields.Integer(dump_only=True)
    code = fields.Str(allow_none=True)
    access_url = fields.Url(allow_none=True)
    is_active = fields.Boolean(default=False)

    # For event level access this holds the max. uses
    tickets_number = fields.Integer(validate=lambda n: n >= 0, allow_none=True)

    min_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    valid_from = fields.DateTime(required=True)
    valid_till = fields.DateTime(required=True)
    used_for = fields.Str(allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.access_code_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'access_code_id': '<id>'},
                         schema='EventSchemaPublic',
                         type_='event')
    marketer = Relationship(attribute='user',
                            self_view='v1.access_code_user',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'access_code_id': '<id>'},
                            schema='UserSchemaPublic',
                            type_='user')
    tickets = Relationship(attribute='tickets',
                           self_view='v1.access_code_tickets',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'access_code_id': '<id>'},
                           schema='TicketSchemaPublic',
                           many=True,
                           type_='ticket')

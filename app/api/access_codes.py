from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema

from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required, current_identity
from app.models import db
from app.api.helpers.exceptions import UnprocessableEntity
from app.models.access_code import AccessCode
from app.models.user import User
from app.models.event import Event
from app.models.ticket import Ticket
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.query import event_query


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
                         schema='EventSchema',
                         type_='event')
    marketer = Relationship(attribute='user',
                            self_view='v1.access_code_user',
                            self_view_kwargs={'id': '<id>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'access_code_id': '<id>'},
                            schema='UserSchema',
                            type_='user')
    tickets = Relationship(attribute='tickets',
                           self_view='v1.access_code_tickets',
                           self_view_kwargs={'id': '<id>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'access_code_id': '<id>'},
                           schema='TicketSchema',
                           many=True,
                           type_='ticket')


class AccessCodeList(ResourceList):
    """
    List and create AccessCodes
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        """
        query method for access code list
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(AccessCode)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            query_ = query_.join(User).filter(User.id == user.id)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            # access_code - ticket :: many-to-many relationship
            query_ = AccessCode.query.filter(AccessCode.tickets.any(id=ticket.id))
        return query_

    def before_post(self, args, kwargs, data):
        """
        method to add user_id to view_kwargs before post
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        kwargs['user_id'] = current_identity.id

    def before_create_object(self, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            data['event_id'] = ticket.event_id
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            data['event_id'] = event.id
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            data['event_id'] = event.id
        data['user_id'] = current_identity.id

    def after_create_object(self, obj, data, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            ticket.access_codes.append(obj)
            self.session.commit()

    view_kwargs = True
    decorators = (jwt_required, )
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object,
                      'after_create_object': after_create_object
                  }}


class AccessCodeDetail(ResourceDetail):
    """
    AccessCode detail by id
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if ticket.access_code_id:
                view_kwargs['id'] = ticket.access_code_id
            else:
                view_kwargs['id'] = None

    decorators = (jwt_required, )
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class AccessCodeRelationshipRequired(ResourceRelationship):
    """
    AccessCode Relationship
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}


class AccessCodeRelationshipOptional(ResourceRelationship):
    """
    AccessCode Relationship
    """
    decorators = (jwt_required,)
    schema = AccessCodeSchema
    data_layer = {'session': db.session,
                  'model': AccessCode}

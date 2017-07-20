from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import validates_schema

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.ticket import Ticket, TicketTag, ticket_tags_table
from app.models.event import Event
from app.models.access_code import AccessCode
from app.api.helpers.exceptions import UnprocessableEntity
from app.models.ticket_holder import TicketHolder
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship


class TicketSchema(Schema):
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

        if data['sales_starts_at'] >= data['sales_ends_at']:
            raise UnprocessableEntity({'pointer': '/data/attributes/sales-ends-at'},
                                      "sales-ends-at should be after sales-starts-at")

    @validates_schema
    def validate_quantity(self, data):
        if 'max_order' in data and 'min_order' in data:
            if data['max_order'] < data['min_order']:
                raise UnprocessableEntity({'pointer': '/data/attributes/max-order'},
                                          "max-order should be greater than min-order")

        if 'quantity' in data and 'min_order' in data:
            if data['quantity'] < data['min_order']:
                raise UnprocessableEntity({'pointer': '/data/attributes/quantity'},
                                          "quantity should be greater than min-order")

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    description = fields.Str(allow_none=True)
    type = fields.Str(required=True)
    price = fields.Float(validate=lambda n: n >= 0, allow_none=True)
    quantity = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    is_description_visible = fields.Boolean(default=False)
    position = fields.Integer(allow_none=True)
    is_fee_absorbed = fields.Boolean()
    sales_starts_at = fields.DateTime(required=True)
    sales_ends_at = fields.DateTime(required=True)
    is_hidden = fields.Boolean(default=False)
    min_order = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    max_order = fields.Integer(validate=lambda n: n >= 0, allow_none=True)
    event = Relationship(attribute='event',
                         self_view='v1.ticket_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'ticket_id': '<id>'},
                         schema='EventSchema',
                         type_='event')
    ticket_tags = Relationship(attribute='tags',
                               self_view='v1.ticket_ticket_tag',
                               self_view_kwargs={'id': '<id>'},
                               related_view='v1.ticket_tag_list',
                               related_view_kwargs={'ticket_id': '<id>'},
                               schema='TicketTagSchema',
                               type_='ticket-tag')
    access_codes = Relationship(attribute='access_codes',
                                self_view='v1.ticket_access_code',
                                self_view_kwargs={'id': '<id>'},
                                related_view='v1.access_code_list',
                                related_view_kwargs={'ticket_id': '<id>'},
                                schema='AccessCodeSchema',
                                many=True,
                                type_='access-code')


class TicketList(ResourceList):
    """
    Create and List Tickets
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        query_ = self.session.query(Ticket)
        if view_kwargs.get('ticket_tag_id'):
            ticket_tag = safe_query(self, TicketTag, 'id', view_kwargs['ticket_tag_id'], 'ticket_tag_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_tag_id=ticket_tag.id)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.join(Event).filter(Event.id == event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.join(Event).filter(Event.id == event.id)
        if view_kwargs.get('access_code_id'):
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            # access_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.access_codes.any(id=access_code.id))

        return query_

    def before_create_object(self, data, view_kwargs):
        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=Ticket, methods="POST",
                  check=lambda a: a.get('event_id') or a.get('event_identifier')), )
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object
                  }}


class TicketDetail(ResourceDetail):
    """
    Ticket Resource
    """
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('attendee_id') is not None:
            attendee = safe_query(self, TicketHolder, 'id', view_kwargs['attendee_id'], 'attendee_id')
            if attendee.ticket_id is not None:
                view_kwargs['id'] = attendee.ticket_id
            else:
                view_kwargs['id'] = None

    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=Ticket, methods="PATCH,DELETE"), )
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket,
                  'methods': {
                      'before_get_object': before_get_object
                  }}


class TicketRelationshipRequired(ResourceRelationship):
    """
    Tickets Relationship (Required)
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketRelationshipOptional(ResourceRelationship):
    """
    Tickets Relationship (Optional)
    """
    decorators = (jwt_required,)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}

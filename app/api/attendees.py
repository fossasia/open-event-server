from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.models import db
from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.models.ticket import Ticket
from app.models.event import Event
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import dasherize
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship


class AttendeeSchema(Schema):
    """
    Api schema for Ticket Holder Model
    """

    class Meta:
        """
        Meta class for Attendee API Schema
        """
        type_ = 'attendee'
        self_view = 'v1.attendee_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    firstname = fields.Str(required=True)
    lastname = fields.Str(allow_none=True)
    email = fields.Str(allow_none=True)
    address = fields.Str(allow_none=True)
    city = fields.Str(allow_none=True)
    state = fields.Str(allow_none=True)
    country = fields.Str(allow_none=True)
    is_checked_in = fields.Boolean()
    pdf_url = fields.Url(required=True)
    ticket = Relationship(attribute='ticket',
                          self_view='v1.attendee_ticket',
                          self_view_kwargs={'id': '<id>'},
                          related_view='v1.ticket_detail',
                          related_view_kwargs={'attendee_id': '<id>'},
                          schema='TicketSchema',
                          type_='ticket')
    event = Relationship(attribute='event',
                         self_view='v1.attendee_event',
                         self_view_kwargs={'id': '<id>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'attendee_id': '<id>'},
                         schema='EventSchema',
                         type_='event')

class AttendeeList(ResourceList):
    """
    List and create Attendees
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)

    def query(self, view_kwargs):
        query_ = self.session.query(TicketHolder)
        if view_kwargs.get('order_id') and view_kwargs.get('ticket_id'):
            order = safe_query(self, Order, 'id', view_kwargs['order_id'], 'order_id')
            query_ = query_.join(Order).filter(Order.id == order.id)

            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            query_ = query_.join(Ticket).filter(Ticket.id == ticket.id)
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
            query_ = query_.filter_by(event_id=event.id)
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
            query_ = query_.filter_by(event_id=event.id)
        return query_

    def before_create_object(self, data, view_kwargs):
        """
        method to create object before post
        :param data:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('order_id') and view_kwargs.get('ticket_id'):
            order = safe_query(self, Order, 'id', view_kwargs['order_id'], 'order_id')
            data['order_id'] = order.id

            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            data['ticket_id'] = ticket.id

        event = None
        if view_kwargs.get('event_id'):
            event = safe_query(self, Event, 'id', view_kwargs['event_id'], 'event_id')
        elif view_kwargs.get('event_identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['event_identifier'], 'event_identifier')
        if event:
            data['event_id'] = event.id

    view_kwargs = True
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder,
                  'methods': {
                      'query': query,
                      'before_create_object': before_create_object}}


class AttendeeDetail(ResourceDetail):
    """
    Attendee detail by id
    """
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}


class AttendeeRelationshipRequired(ResourceRelationship):
    """
    Attendee Relationship (Required)
    """
    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}


class AttendeeRelationshipOptional(ResourceRelationship):
    """
    Attendee Relationship(Optional)
    """
    decorators = (api.has_permission('is_user_itself', fetch="user_id", fetch_as="id", model=TicketHolder),)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}

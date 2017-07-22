from flask_jwt import current_identity
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields

from app.api.bootstrap import api
from app.api.helpers.exceptions import ForbiddenException
from app.api.helpers.permission_manager import has_access
from app.models import db
from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.models.ticket import Ticket
from app.models.event import Event
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import dasherize
from app.api.helpers.db import safe_query
from app.api.helpers.utilities import require_relationship
from app.api.helpers.query import event_query


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


class AttendeeListPost(ResourceList):
    """
       List and create Attendees through direct URL
    """

    def before_post(self, args, kwargs, data):
        require_relationship(['ticket', 'event'], data)

    def before_get(self, args, kwargs):
        if not has_access('is_admin'):
            raise ForbiddenException({'source': ''}, 'You are not authorized to access this.')

    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}


class AttendeeList(ResourceList):
    """
    List Attendees
    """
    def query(self, view_kwargs):
        query_ = self.session.query(TicketHolder)
        if view_kwargs.get('order_id'):
            order = safe_query(self, Order, 'id', view_kwargs['order_id'], 'order_id')
            query_ = query_.join(Order).filter(Order.id == order.id)
        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            query_ = query_.join(Ticket).filter(Ticket.id == ticket.id)
        query_ = event_query(self, query_, view_kwargs)
        return query_

    view_kwargs = True
    decorators = (api.has_permission('is_registrar', fetch="event_id", fetch_as="event_id", fetch_key_url="order_id",
                                     model=Order),)
    methods = ['GET', ]
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder,
                  'methods': {
                      'query': query
                  }}


class AttendeeDetail(ResourceDetail):
    """
    Attendee detail by id
    """
    def before_get_object(self, view_kwargs):
        attendee = safe_query(self, TicketHolder, 'id', view_kwargs['id'], 'attendee_id')
        if not has_access('is_registrar_or_user_itself', user_id=current_identity.id, event_id=attendee.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

    def before_delete_object(self, obj, kwargs):
        if not has_access('is_registrar', event_id=obj.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

    def before_update_object(self, obj, data, kwargs):
        if not has_access('is_registrar', event_id=obj.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder,
                  'methods': {
                      'before_get_object': before_get_object,
                      'before_update_object': before_update_object,
                      'before_delete_object': before_delete_object
                  }}


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

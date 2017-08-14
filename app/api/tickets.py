from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.tickets import TicketSchema
from app.models import db
from app.models.access_code import AccessCode
from app.models.order import Order
from app.models.ticket import Ticket, TicketTag, ticket_tags_table
from app.models.ticket_holder import TicketHolder


class TicketListPost(ResourceList):
    """
    Create and List Tickets
    """
    def before_post(self, args, kwargs, data):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound({'parameter': 'event_id'},
                                 "Event: {} not found".format(data['event_id']))

    schema = TicketSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketList(ResourceList):
    """
    List Tickets based on different params
    """

    def query(self, view_kwargs):
        query_ = self.session.query(Ticket)
        if view_kwargs.get('ticket_tag_id'):
            ticket_tag = safe_query(self, TicketTag, 'id', view_kwargs['ticket_tag_id'], 'ticket_tag_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_tag_id=ticket_tag.id)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('access_code_id'):
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            # access_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.access_codes.any(id=access_code.id))

        if view_kwargs.get('order_identifier'):
            order = safe_query(self, Order, 'identifer', view_kwargs['order_identifier'],
                                                 'order_identifer')
            ticket_ids = []
            for ticket in order.tickets:
                ticket_ids.append(ticket.id)
            query_ = query_.filter(Ticket.id.in_(tuple(ticket_ids)))

        return query_

    view_kwargs = True
    methods = ['GET', ]
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                  fetch_as="event_id", model=Ticket, methods="POST",
                  check=lambda a: a.get('event_id') or a.get('event_identifier')),)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket,
                  'methods': {
                      'query': query,
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
                  fetch_as="event_id", model=Ticket, methods="PATCH,DELETE"),)
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
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                                     fetch_as="event_id", model=Ticket, methods="PATCH"),)
    methods = ['GET', 'PATCH']
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketRelationshipOptional(ResourceRelationship):
    """
    Tickets Relationship (Optional)
    """
    decorators = (api.has_permission('is_coorganizer', fetch='event_id',
                                     fetch_as="event_id", model=Ticket, methods="PATCH,DELETE"),)
    schema = TicketSchema
    data_layer = {'session': db.session,
                  'model': Ticket}

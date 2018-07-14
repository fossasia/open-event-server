from flask import request, current_app
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from flask_jwt import current_identity as current_user, _jwt_required

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.permission_manager import has_access
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.tickets import TicketSchema, TicketSchemaPublic
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.models.order import Order
from app.models.ticket import Ticket, TicketTag, ticket_tags_table
from app.models.event import Event
from app.models.ticket_holder import TicketHolder
from app.api.helpers.exceptions import ConflictException, MethodNotAllowed
from app.api.helpers.db import get_count

class TicketListPost(ResourceList):
    """
    Create and List Tickets
    """
    def before_post(self, args, kwargs, data):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            raise ObjectNotFound({'parameter': 'event_id'},
                                 "Event: {} not found".format(data['event']))

        if get_count(db.session.query(Ticket.id).filter_by(name=data['name'], event_id=int(data['event']),
                                                           deleted_at=None)) > 0:
            raise ConflictException({'pointer': '/data/attributes/name'}, "Ticket already exists")

        if get_count(db.session.query(Event).filter_by(id=int(data['event']), is_ticketing_enabled=False)) > 0:
            raise MethodNotAllowed({'parameter': 'event_id'}, "Ticketing is disabled for this Event")

    schema = TicketSchema
    methods = ['POST', ]
    data_layer = {'session': db.session,
                  'model': Ticket}


class TicketList(ResourceList):
    """
    List Tickets based on different params
    """
    def before_get(self, args, view_kwargs):
        """
        before get method to get the resource id for assigning schema
        :param args:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('ticket_tag_id') or view_kwargs.get('access_code_id') or view_kwargs.get('order_identifier'):
            self.schema = TicketSchemaPublic

    def query(self, view_kwargs):
        """
        query method for resource list
        :param view_kwargs:
        :return:
        """

        if 'Authorization' in request.headers:
            _jwt_required(current_app.config['JWT_DEFAULT_REALM'])
            if current_user.is_super_admin or current_user.is_admin:
                query_ = self.session.query(Ticket)
            elif view_kwargs.get('event_id') and has_access('is_organizer', event_id=view_kwargs['event_id']):
                query_ = self.session.query(Ticket)
            else:
                query_ = self.session.query(Ticket).filter_by(is_hidden=False)
        else:
            query_ = self.session.query(Ticket).filter_by(is_hidden=False)

        if view_kwargs.get('ticket_tag_id'):
            ticket_tag = safe_query(self, TicketTag, 'id', view_kwargs['ticket_tag_id'], 'ticket_tag_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_tag_id=ticket_tag.id)
        query_ = event_query(self, query_, view_kwargs)
        if view_kwargs.get('access_code_id'):
            access_code = safe_query(self, AccessCode, 'id', view_kwargs['access_code_id'], 'access_code_id')
            # access_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.access_codes.any(id=access_code.id))

        if view_kwargs.get('discount_code_id'):
            discount_code = safe_query(self, DiscountCode, 'id', view_kwargs['discount_code_id'], 'discount_code_id')
            # discount_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.discount_codes.any(id=discount_code.id))

        if view_kwargs.get('order_identifier'):
            order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
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
    def before_get(self, args, view_kwargs):
        """
        before get method to get the resource id for assigning schema
        :param args:
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('attendee_id'):
            self.schema = TicketSchemaPublic

    def before_get_object(self, view_kwargs):
        """
        before get object method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
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

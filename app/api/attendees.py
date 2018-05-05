from flask_jwt import current_identity
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship

from app.api.bootstrap import api
from app.api.helpers.db import safe_query
from app.api.helpers.exceptions import ForbiddenException, UnprocessableEntity
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.attendees import AttendeeSchema
from app.models import db
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder
from app.models.user import User


class AttendeeListPost(ResourceList):
    """
       List and create Attendees through direct URL
    """

    def before_post(self, args, kwargs, data):
        """
        Before post method to check for required relationship and proper permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['ticket', 'event'], data)

        ticket = db.session.query(Ticket).filter_by(id=int(data['ticket'])).first()
        if ticket is None:
            raise UnprocessableEntity({'pointer': '/data/relationships/ticket'}, "Invalid Ticket")
        if ticket.event_id != int(data['event']):
            raise UnprocessableEntity({'pointer': '/data/relationships/ticket'}, "Ticket belongs to a different Event")

    decorators = (jwt_required,)
    methods = ['POST']
    schema = AttendeeSchema
    data_layer = {'session': db.session,
                  'model': TicketHolder}


class AttendeeList(ResourceList):
    """
    List Attendees
    """
    def query(self, view_kwargs):
        """
        query method for Attendees List
        :param view_kwargs:
        :return:
        """
        query_ = self.session.query(TicketHolder)

        if view_kwargs.get('order_identifier'):
            order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
            if not has_access('is_registrar', event_id=order.event_id) or not has_access('is_user_itself',
                                                                                         id=order.user_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Order).filter(Order.id == order.id)

        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            if not has_access('is_registrar', event_id=ticket.event_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Ticket).filter(Ticket.id == ticket.id)

        if view_kwargs.get('user_id'):
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User, User.email == TicketHolder.email).filter(User.id == user.id)

        query_ = event_query(self, query_, view_kwargs, permission='is_registrar')
        return query_

    view_kwargs = True
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
        """
        before get object method for attendee detail
        :param view_kwargs:
        :return:
        """
        attendee = safe_query(self, TicketHolder, 'id', view_kwargs['id'], 'attendee_id')
        if not has_access('is_registrar_or_user_itself', user_id=current_identity.id, event_id=attendee.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

    def before_delete_object(self, obj, kwargs):
        """
        before delete object method for attendee detail
        :param obj:
        :param kwargs:
        :return:
        """
        if not has_access('is_registrar', event_id=obj.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

    def before_update_object(self, obj, data, kwargs):
        """
        before update object method for attendee detail
        :param obj:
        :param data:
        :param kwargs:
        :return:
        """
        if not has_access('is_registrar', event_id=obj.event_id):
            raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

        if 'is_checked_in' in data and data['is_checked_in']:
            if 'checkin_times' not in data:
                raise UnprocessableEntity({'pointer': '/data/attributes/checkin_times'},
                                          "Check in time missing while trying to check in attendee")
            else:
                if obj.checkin_times and data['checkin_times'] not in obj.checkin_times.split(","):
                    data['checkin_times'] = '{},{}'.format(obj.checkin_times, data['checkin_times'])

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

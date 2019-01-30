from datetime import datetime

from flask import Blueprint, request, jsonify, abort, make_response
from flask_jwt import current_identity, jwt_required
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.helpers.db import safe_query, get_count
from app.api.helpers.exceptions import (
    ConflictException,
    ForbiddenException,
    UnprocessableEntity,
)
from app.api.helpers.mail import send_email_to_attendees
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

attendee_misc_routes = Blueprint('attendee_misc', __name__, url_prefix='/v1')


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

        ticket = db.session.query(Ticket).filter_by(
            id=int(data['ticket']), deleted_at=None
            ).first()
        if ticket is None:
            raise UnprocessableEntity(
                {'pointer': '/data/relationships/ticket'}, "Invalid Ticket"
                )
        if ticket.event_id != int(data['event']):
            raise UnprocessableEntity(
                {'pointer': '/data/relationships/ticket'},
                "Ticket belongs to a different Event"
            )
        # Check if the ticket is already sold out or not.
        if get_count(db.session.query(TicketHolder.id).
                     filter_by(ticket_id=int(data['ticket']), deleted_at=None)) >= ticket.quantity:
            raise ConflictException(
                {'pointer': '/data/attributes/ticket_id'},
                "Ticket already sold out"
            )

        if 'device_name_checkin' in data and data['device_name_checkin'] is not None:
            if 'is_checked_in' not in data or not data['is_checked_in']:
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Attendee needs to be checked in first"
                )
            elif 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing"
                )
            elif len(data['checkin_times'].split(",")) != len(data['device_name_checkin'].split(",")):
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing for the corresponding device name"
                )

        if 'checkin_times' in data:
            if 'device_name_checkin' not in data or data['device_name_checkin'] is None:
                data['device_name_checkin'] = '-'

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
            if not has_access('is_registrar', event_id=order.event_id) and not has_access('is_user_itself',
                                                                                         user_id=order.user_id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Order).filter(Order.id == order.id)

        if view_kwargs.get('ticket_id'):
            ticket = safe_query(self, Ticket, 'id', view_kwargs['ticket_id'], 'ticket_id')
            # if not has_access('is_registrar', event_id=ticket.event_id):
            #     raise ForbiddenException({'source': ''}, 'Access Forbidden')
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
#         if not has_access('is_registrar', event_id=obj.event_id):
#         raise ForbiddenException({'source': 'User'}, 'You are not authorized to access this.')

        if 'device_name_checkin' in data:
            if 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntity(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing"
                )

        if 'is_checked_in' in data and data['is_checked_in']:
            if 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntity({'pointer': '/data/attributes/checkin_times'},
                                          "Check in time missing while trying to check in attendee")
            else:
                if obj.checkin_times and data['checkin_times'] not in obj.checkin_times.split(","):
                    data['checkin_times'] = '{},{}'.format(obj.checkin_times, data['checkin_times'])
                elif obj.checkin_times and data['checkin_times'] in obj.checkin_times.split(","):
                    raise UnprocessableEntity(
                        {'pointer': '/data/attributes/checkin_times'},
                        "Check in time already present"
                    )

                if 'device_name_checkin' in data and data['device_name_checkin'] is not None:
                    if obj.device_name_checkin is not None:
                        data['device_name_checkin'] = '{},{}'.format(obj.device_name_checkin,
                                                                     data['device_name_checkin'])

                    if len(data['checkin_times'].split(",")) != len(data['device_name_checkin'].split(",")):
                        raise UnprocessableEntity(
                            {'pointer': '/data/attributes/device_name_checkin'},
                            "Check in Time missing for the corresponding device name"
                        )
                else:
                    if obj.device_name_checkin is not None:
                        data['device_name_checkin'] = '{},{}'.format(obj.device_name_checkin, '-')
                    else:
                        data['device_name_checkin'] = '-'

        if 'is_checked_out' in data and data['is_checked_out']:
            attendee = safe_query(db, TicketHolder, 'id', kwargs['id'], 'attendee_id')
            if not attendee.is_checked_out:
                checkout_times = obj.checkout_times.split(',') if obj.checkout_times else []
                checkout_times.append(str(datetime.utcnow()))
                data['checkout_times'] = ','.join(checkout_times)

        if 'attendee_notes' in data:
            if obj.attendee_notes and data['attendee_notes'] not in obj.attendee_notes.split(","):
                data['attendee_notes'] = '{},{}'.format(obj.attendee_notes, data['attendee_notes'])

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


@attendee_misc_routes.route('/attendees/send-receipt', methods=['POST'])
@jwt_required
def send_receipt():
    """
    Send receipts to attendees related to the provided order.
    :return:
    """
    order_identifier = request.json.get('order-identifier')
    if order_identifier:
        try:
            order = db.session.query(Order).filter_by(identifier=order_identifier).one()
        except NoResultFound:
            raise ObjectNotFound({'parameter': '{identifier}'}, "Order not found")

        if (order.user_id != current_identity.id) and (not has_access('is_registrar', event_id=order.event_id)):
            abort(
                make_response(jsonify(error="You need to be the event organizer or order buyer to send receipts."), 403)
            )
        elif order.status != 'completed':
            abort(
                make_response(jsonify(error="Cannot send receipt for an incomplete order"), 409)
            )
        else:
            send_email_to_attendees(order, current_identity.id)
            return jsonify(message="receipt sent to attendees")
    else:
        abort(
            make_response(jsonify(error="Order identifier missing"), 422)
        )

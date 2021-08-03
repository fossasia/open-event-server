import datetime

from flask_jwt_extended import current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from sqlalchemy import and_, or_

from app.api.bootstrap import api
from app.api.helpers.custom_forms import validate_custom_form_constraints_request
from app.api.helpers.db import safe_query, safe_query_by_id, safe_query_kwargs
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError
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
from app.settings import get_settings


def get_sold_and_reserved_tickets_count(ticket_id):
    order_expiry_time = get_settings()['order_expiry_time']
    return (
        db.session.query(TicketHolder.id)
        .join(Order)
        .filter(
            TicketHolder.ticket_id == ticket_id,
            TicketHolder.order_id == Order.id,
            TicketHolder.deleted_at.is_(None),
        )
        .filter(
            or_(
                Order.status == 'placed',
                Order.status == 'completed',
                and_(
                    Order.status == 'initializing',
                    Order.created_at + datetime.timedelta(minutes=order_expiry_time)
                    > datetime.datetime.utcnow(),
                ),
                and_(
                    Order.status == 'pending',
                    Order.created_at + datetime.timedelta(minutes=30 + order_expiry_time)
                    > (datetime.datetime.utcnow()),
                ),
            ),
        )
        .count()
    )


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

        ticket = (
            db.session.query(Ticket)
            .filter_by(id=int(data['ticket']), deleted_at=None)
            .first()
        )
        if ticket is None:
            raise UnprocessableEntityError(
                {'pointer': '/data/relationships/ticket'}, "Invalid Ticket"
            )
        if ticket.event_id != int(data['event']):
            raise UnprocessableEntityError(
                {'pointer': '/data/relationships/ticket'},
                "Ticket belongs to a different Event",
            )
        # Check if the ticket is already sold out or not.
        ticket.raise_if_unavailable()

        if 'device_name_checkin' in data and data['device_name_checkin'] is not None:
            if 'is_checked_in' not in data or not data['is_checked_in']:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Attendee needs to be checked in first",
                )
            if 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing",
                )
            if len(data['checkin_times'].split(",")) != len(
                data['device_name_checkin'].split(",")
            ):
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing for the corresponding device name",
                )

        if 'checkin_times' in data:
            if 'device_name_checkin' not in data or data['device_name_checkin'] is None:
                data['device_name_checkin'] = '-'

    decorators = (jwt_required,)
    methods = ['POST']
    schema = AttendeeSchema
    data_layer = {'session': db.session, 'model': TicketHolder}


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
            order = safe_query_kwargs(
                Order,
                view_kwargs,
                'order_identifier',
                'identifier',
            )

            is_coorganizer = has_access(
                'is_coorganizer',
                event_id=order.event_id,
            )
            if not (
                is_coorganizer
                or current_user.id == order.user_id
                or order.is_attendee(current_user)
            ):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Order).filter(Order.id == order.id)
            if not is_coorganizer and current_user.id != order.user_id:
                query_ = query_.filter(TicketHolder.user == current_user)

        if view_kwargs.get('ticket_id'):
            ticket = safe_query_kwargs(Ticket, view_kwargs, 'ticket_id')
            # if not has_access('is_registrar', event_id=ticket.event_id):
            #     raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.join(Ticket).filter(Ticket.id == ticket.id)

        if view_kwargs.get('user_id'):
            user = safe_query_kwargs(User, view_kwargs, 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenError({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User, User.email == TicketHolder.email).filter(
                User.id == user.id
            )

        query_ = event_query(query_, view_kwargs, restrict=True)
        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {
        'session': db.session,
        'model': TicketHolder,
        'methods': {'query': query},
    }


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
        attendee = safe_query(TicketHolder, 'id', view_kwargs['id'], 'attendee_id')
        if not has_access(
            'is_registrar_or_user_itself',
            user_id=current_user.id,
            event_id=attendee.event_id,
        ):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    def before_delete_object(self, obj, kwargs):
        """
        before delete object method for attendee detail
        :param obj:
        :param kwargs:
        :return:
        """
        if not has_access('is_registrar', event_id=obj.event_id):
            raise ForbiddenError(
                {'source': 'User'}, 'You are not authorized to access this.'
            )

    def before_update_object(self, obj, data, kwargs):
        """
        before update object method for attendee detail
        :param obj:
        :param data:
        :param kwargs:
        :return:
        """
        order = safe_query_by_id(Order, obj.order_id)

        if not (current_user.is_staff or current_user.id == order.user_id):
            raise ForbiddenError(
                'Only admin or that user itself can update attendee info',
            )

        if order.status != 'initializing' and (
            'checkin_times' not in data
        ):
            raise UnprocessableEntityError(
                {'pointer': '/data/id'},
                "Attendee can't be updated because the corresponding order is not in initializing state",
            )

        if 'device_name_checkin' in data:
            if 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/device_name_checkin'},
                    "Check in Times missing",
                )

        if 'is_checked_in' in data and data['is_checked_in']:
            if 'checkin_times' not in data or data['checkin_times'] is None:
                raise UnprocessableEntityError(
                    {'pointer': '/data/attributes/checkin_times'},
                    "Check in time missing while trying to check in attendee",
                )
            if obj.checkin_times and data['checkin_times'] not in obj.checkin_times.split(
                ","
            ):
                data['checkin_times'] = '{},{}'.format(
                    obj.checkin_times, data['checkin_times']
                )

            if 'device_name_checkin' in data and data['device_name_checkin'] is not None:
                if obj.device_name_checkin is not None:
                    data['device_name_checkin'] = '{},{}'.format(
                        obj.device_name_checkin, data['device_name_checkin']
                    )

                if len(data['checkin_times'].split(",")) != len(
                    data['device_name_checkin'].split(",")
                ):
                    raise UnprocessableEntityError(
                        {'pointer': '/data/attributes/device_name_checkin'},
                        "Check in Time missing for the corresponding device name",
                    )
            else:
                if obj.device_name_checkin is not None:
                    data['device_name_checkin'] = '{},{}'.format(
                        obj.device_name_checkin, '-'
                    )
                else:
                    data['device_name_checkin'] = '-'

        if 'is_checked_out' in data and data['is_checked_out']:
            attendee = safe_query(TicketHolder, 'id', kwargs['id'], 'attendee_id')
            if not attendee.is_checked_out:
                checkout_times = (
                    obj.checkout_times.split(',') if obj.checkout_times else []
                )
                checkout_times.append(str(datetime.datetime.utcnow()))
                data['checkout_times'] = ','.join(checkout_times)

        if 'attendee_notes' in data:
            if obj.attendee_notes and data[
                'attendee_notes'
            ] not in obj.attendee_notes.split(","):
                data['attendee_notes'] = '{},{}'.format(
                    obj.attendee_notes, data['attendee_notes']
                )

        data['complex_field_values'] = (
            validate_custom_form_constraints_request(
                'attendee', self.resource.schema, obj, data
            )
            if obj.event.is_ticket_form_enabled
            else None
        )

    decorators = (jwt_required,)
    schema = AttendeeSchema
    data_layer = {
        'session': db.session,
        'model': TicketHolder,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
            'before_delete_object': before_delete_object,
        },
    }


class AttendeeRelationshipRequired(ResourceRelationship):
    """
    Attendee Relationship (Required)
    """

    decorators = (jwt_required,)
    methods = ['GET', 'PATCH']
    schema = AttendeeSchema
    data_layer = {'session': db.session, 'model': TicketHolder}


class AttendeeRelationshipOptional(ResourceRelationship):
    """
    Attendee Relationship(Optional)
    """

    decorators = (
        api.has_permission(
            'is_user_itself', fetch="user_id", fetch_as="id", model=TicketHolder
        ),
    )
    schema = AttendeeSchema
    data_layer = {'session': db.session, 'model': TicketHolder}

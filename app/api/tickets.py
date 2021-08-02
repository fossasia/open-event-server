from flask import Blueprint, jsonify
from flask_jwt_extended import current_user, verify_jwt_in_request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.attendees import get_sold_and_reserved_tickets_count
from app.api.bootstrap import api
from app.api.helpers.db import get_count, safe_query_kwargs
from app.api.helpers.errors import ConflictError, ForbiddenError, UnprocessableEntityError
from app.api.helpers.permission_manager import has_access, is_logged_in
from app.api.helpers.query import event_query
from app.api.helpers.utilities import require_relationship
from app.api.schema.tickets import TicketSchema, TicketSchemaPublic
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.order import Order
from app.models.ticket import Ticket, TicketTag, ticket_tags_table
from app.models.ticket_holder import TicketHolder

tickets_routes = Blueprint('tickets_routes', __name__, url_prefix='/v1/events')


@tickets_routes.route('/<id>/tickets/availability')
def get_stock(id):
    event_id = id

    if not id.isnumeric():
        event_id = Event.query.filter_by(identifier=id).first_or_404().id

    tickets = Ticket.query.filter_by(
        event_id=event_id, deleted_at=None, is_hidden=False
    ).all()
    stock = []
    for ticket in tickets:
        availability = {}
        total_count = ticket.quantity - get_sold_and_reserved_tickets_count(ticket.id)
        availability["id"] = ticket.id
        availability["name"] = ticket.name
        availability["quantity"] = ticket.quantity
        availability["available"] = max(0, total_count)
        stock.append(availability)

    return jsonify(stock)


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
            raise ObjectNotFound(
                {'parameter': 'event_id'}, "Event: {} not found".format(data['event'])
            )

        if (
            get_count(
                db.session.query(Ticket.id).filter_by(
                    name=data['name'], event_id=int(data['event']), deleted_at=None
                )
            )
            > 0
        ):
            raise ConflictError(
                {'pointer': '/data/attributes/name'}, "Ticket already exists"
            )

    def before_create_object(self, data, view_kwargs):
        """
        before create method to check if paid ticket has a paymentMethod enabled
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('event'):
            try:
                event = (
                    db.session.query(Event)
                    .filter_by(id=data['event'], deleted_at=None)
                    .one()
                )
            except NoResultFound:
                raise UnprocessableEntityError(
                    {'event_id': data['event']}, "Event does not exist"
                )

            if data.get('type') == 'paid' or data.get('type') == 'donation':
                if not event.is_payment_enabled():
                    raise UnprocessableEntityError(
                        {'event_id': data['event']},
                        "Event having paid ticket must have a payment method",
                    )

            if data.get('sales_ends_at') > event.ends_at:
                raise UnprocessableEntityError(
                    {'sales_ends_at': '/data/attributes/sales-ends-at'},
                    f"End of ticket sales date of '{data.get('name')}' cannot be after end of event date",
                )

    schema = TicketSchema
    methods = [
        'POST',
    ]
    data_layer = {
        'session': db.session,
        'model': Ticket,
        'methods': {
            'before_create_object': before_create_object,
            'before_post': before_post,
        },
    }


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
        if (
            view_kwargs.get('ticket_tag_id')
            or view_kwargs.get('access_code_id')
            or view_kwargs.get('order_identifier')
        ):
            self.schema = TicketSchemaPublic

    def query(self, view_kwargs):
        """
        query method for resource list
        :param view_kwargs:
        :return:
        """

        if is_logged_in():
            verify_jwt_in_request()
            if current_user.is_super_admin or current_user.is_admin:
                query_ = self.session.query(Ticket)
            elif view_kwargs.get('event_id') and has_access(
                'is_organizer', event_id=view_kwargs['event_id']
            ):
                query_ = self.session.query(Ticket)
            else:
                query_ = self.session.query(Ticket).filter_by(is_hidden=False)
        else:
            query_ = self.session.query(Ticket).filter_by(is_hidden=False)

        if view_kwargs.get('ticket_tag_id'):
            ticket_tag = safe_query_kwargs(TicketTag, view_kwargs, 'ticket_tag_id')
            query_ = query_.join(ticket_tags_table).filter_by(ticket_tag_id=ticket_tag.id)
        query_ = event_query(query_, view_kwargs)
        if view_kwargs.get('access_code_id'):
            access_code = safe_query_kwargs(AccessCode, view_kwargs, 'access_code_id')
            # access_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.access_codes.any(id=access_code.id))

        if view_kwargs.get('discount_code_id'):
            discount_code = safe_query_kwargs(
                DiscountCode,
                view_kwargs,
                'discount_code_id',
            )
            # discount_code - ticket :: many-to-many relationship
            query_ = Ticket.query.filter(Ticket.discount_codes.any(id=discount_code.id))

        if view_kwargs.get('order_identifier'):
            order = safe_query_kwargs(
                Order, view_kwargs, 'order_identifier', 'identifier'
            )
            ticket_ids = []
            for ticket in order.tickets:
                ticket_ids.append(ticket.id)
            query_ = query_.filter(Ticket.id.in_(tuple(ticket_ids)))

        return query_

    view_kwargs = True
    methods = [
        'GET',
    ]
    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=Ticket,
            methods="POST",
            check=lambda a: a.get('event_id') or a.get('event_identifier'),
        ),
    )
    schema = TicketSchema
    data_layer = {
        'session': db.session,
        'model': Ticket,
        'methods': {
            'query': query,
        },
    }


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
            attendee = safe_query_kwargs(TicketHolder, view_kwargs, 'attendee_id')
            if attendee.ticket_id is not None:
                view_kwargs['id'] = attendee.ticket_id
            else:
                view_kwargs['id'] = None

    def before_update_object(self, ticket, data, view_kwargs):
        """
        method to check if paid ticket has payment method before updating ticket object
        :param ticket:
        :param data:
        :param view_kwargs:
        :return:
        """
        if ticket.type == 'paid' or ticket.type == 'donation':
            try:
                event = (
                    db.session.query(Event)
                    .filter_by(id=ticket.event.id, deleted_at=None)
                    .one()
                )
            except NoResultFound:
                raise UnprocessableEntityError(
                    {'event_id': ticket.event.id}, "Event does not exist"
                )
            if not event.is_payment_enabled():
                raise UnprocessableEntityError(
                    {'event_id': ticket.event.id},
                    "Event having paid ticket must have a payment method",
                )

        if data.get('deleted_at') and ticket.has_current_orders:
            raise ForbiddenError(
                {'param': 'ticket_id'},
                "Can't delete a ticket that has sales",
            )

        if data.get('sales_ends_at') and data['sales_ends_at'] > ticket.event.ends_at:
            raise UnprocessableEntityError(
                {'sales_ends_at': '/data/attributes/sales-ends-at'},
                f"End of ticket sales date of '{ticket.name}' cannot be after end of event date",
            )

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=Ticket,
            methods="PATCH,DELETE",
        ),
    )
    schema = TicketSchema
    data_layer = {
        'session': db.session,
        'model': Ticket,
        'methods': {
            'before_get_object': before_get_object,
            'before_update_object': before_update_object,
        },
    }


class TicketRelationshipRequired(ResourceRelationship):
    """
    Tickets Relationship (Required)
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=Ticket,
            methods="PATCH",
        ),
    )
    methods = ['GET', 'PATCH']
    schema = TicketSchema
    data_layer = {'session': db.session, 'model': Ticket}


class TicketRelationshipOptional(ResourceRelationship):
    """
    Tickets Relationship (Optional)
    """

    decorators = (
        api.has_permission(
            'is_coorganizer',
            fetch='event_id',
            model=Ticket,
            methods="PATCH,DELETE",
        ),
    )
    schema = TicketSchema
    data_layer = {'session': db.session, 'model': Ticket}

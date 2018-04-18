from datetime import datetime

from flask import request, render_template
from flask_jwt import current_identity as current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.data_layers.ChargesLayer import ChargesLayer
from app.api.helpers.db import save_to_db, safe_query
from app.api.helpers.exceptions import ForbiddenException, UnprocessableEntity
from app.api.helpers.files import create_save_pdf
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.mail import send_order_cancel_email
from app.api.helpers.notification import send_notif_to_attendees, send_notif_ticket_purchase_organizer, \
    send_notif_ticket_cancel
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.ticketing import TicketingManager
from app.api.helpers.utilities import dasherize, require_relationship
from app.api.schema.orders import OrderSchema
from app.models import db
from app.models.discount_code import DiscountCode, TICKET
from app.models.order import Order, OrderTicket
from app.models.ticket_holder import TicketHolder


class OrdersListPost(ResourceList):
    """
    OrderListPost class for OrderSchema
    """
    def before_post(self, args, kwargs, data=None):
        """
        before post method to check for required relationship and proper permission
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event', 'ticket_holders'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            data['status'] = 'pending'

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for OrderListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        if data.get('cancel_note'):
            del data['cancel_note']

        # Apply discount only if the user is not event admin
        if data.get('discount') and not has_access('is_coorganizer', event_id=data['event']):
            discount_code = safe_query(self, DiscountCode, 'id', data['discount'], 'discount_code_id')
            if not discount_code.is_active:
                raise UnprocessableEntity({'source': 'discount_code_id'}, "Inactive Discount Code")
            else:
                now = datetime.utcnow()
                valid_from = datetime.strptime(discount_code.valid_from, '%Y-%m-%d %H:%M:%S')
                valid_till = datetime.strptime(discount_code.valid_till, '%Y-%m-%d %H:%M:%S')
                if not (valid_from <= now <= valid_till):
                    raise UnprocessableEntity({'source': 'discount_code_id'}, "Inactive Discount Code")
                if not TicketingManager.match_discount_quantity(discount_code, data['ticket_holders']):
                    raise UnprocessableEntity({'source': 'discount_code_id'}, 'Discount Usage Exceeded')

            if discount_code.event.id != data['event'] and discount_code.user_for == TICKET:
                raise UnprocessableEntity({'source': 'discount_code_id'}, "Invalid Discount Code")

    def after_create_object(self, order, data, view_kwargs):
        """
        after create object method for OrderListPost Class
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        order_tickets = {}
        for holder in order.ticket_holders:
            if holder.id != current_user.id:
                pdf = create_save_pdf(render_template('/pdf/ticket_attendee.html', order=order, holder=holder))
            else:
                pdf = create_save_pdf(render_template('/pdf/ticket_purchaser.html', order=order))
            holder.pdf_url = pdf
            save_to_db(holder)
            if order_tickets.get(holder.ticket_id) is None:
                order_tickets[holder.ticket_id] = 1
            else:
                order_tickets[holder.ticket_id] += 1
        for ticket in order_tickets:
            od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
            save_to_db(od)
        order.quantity = order.get_tickets_count()
        save_to_db(order)
        if not has_access('is_coorganizer', event_id=data['event']):
            TicketingManager.calculate_update_amount(order)
        send_email_to_attendees(order, current_user.id)
        send_notif_to_attendees(order, current_user.id)

        order_url = make_frontend_url(path='/orders/{identifier}'.format(identifier=order.identifier))
        for organizer in order.event.organizers:
            send_notif_ticket_purchase_organizer(organizer, order.invoice_number, order_url, order.event.name)

        data['user_id'] = current_user.id

    methods = ['POST', ]
    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
                  'methods': {'before_create_object': before_create_object,
                              'after_create_object': after_create_object
                              }}


class OrdersList(ResourceList):
    """
    OrderList class for OrderSchema
    """
    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param args:
        :param kwargs:
        :return:
        """
        if kwargs.get('event_id') is None:
            if 'GET' in request.method and has_access('is_admin'):
                pass
            else:
                raise ForbiddenException({'source': ''}, "Admin Access Required")
        elif not has_access('is_coorganizer', event_id=kwargs['event_id']):
            raise ForbiddenException({'source': ''}, "Co-Organizer Access Required")

    def query(self, view_kwargs):
        query_ = self.session.query(Order)
        query_ = event_query(self, query_, view_kwargs)

        return query_

    decorators = (jwt_required,)
    methods = ['GET', ]
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
                  'methods': {
                      'query': query
                  }}


class OrderDetail(ResourceDetail):
    """
    OrderDetail class for OrderSchema
    """
    def before_get_object(self, view_kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if view_kwargs.get('attendee_id'):
            attendee = safe_query(self, TicketHolder, 'id', view_kwargs['attendee_id'], 'attendee_id')
            view_kwargs['order_identifier'] = attendee.order.identifier

        order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')

        if not has_access('is_coorganizer_or_user_itself', event_id=order.event_id, user_id=order.user_id):
            return ForbiddenException({'source': ''}, 'Access Forbidden')

    def before_update_object(self, order, data, view_kwargs):
        """
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        if not has_access('is_admin'):
            for element in data:
                if element != 'status':
                    setattr(data, element, getattr(order, element))

        if not has_access('is_coorganizer', event_id=order.event.id):
            raise ForbiddenException({'pointer': 'data/status'},
                                     "To update status minimum Co-organizer access required")

    def after_update_object(self, order, data, view_kwargs):
        """
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        if order.status == 'cancelled':
            send_order_cancel_email(order)
            send_notif_ticket_cancel(order)

    def before_delete_object(self, order, view_kwargs):
        """
        method to check for proper permissions for deleting
        :param order:
        :param view_kwargs:
        :return:
        """
        if not has_access('is_coorganizer', event_id=order.event.id):
            raise ForbiddenException({'source': ''}, 'Access Forbidden')

    decorators = (jwt_required,)

    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
                  'url_field': 'order_identifier',
                  'id_field': 'identifier',
                  'methods': {
                      'before_update_object': before_update_object,
                      'before_delete_object': before_delete_object,
                      'before_get_object': before_get_object,
                      'after_update_object': after_update_object
                  }}


class OrderRelationship(ResourceRelationship):
    """
    Order relationship
    """
    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order}


class ChargeSchema(Schema):
    """
    ChargeSchema
    """
    class Meta:
        """
        Meta class for ChargeSchema
        """
        type_ = 'charge'
        inflect = dasherize
        self_view = 'v1.charge_list'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    stripe = fields.Str(allow_none=True)


class ChargeList(ResourceList):
    """
    ChargeList ResourceList for ChargesLayer class
    """
    methods = ['POST', ]
    schema = ChargeSchema

    data_layer = {
        'class': ChargesLayer,
        'session': db.session
    }

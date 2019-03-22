from datetime import datetime

from flask import Blueprint, jsonify, request
from flask_jwt import current_identity as current_user
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy.orm.exc import NoResultFound

from app.api.bootstrap import api
from app.api.data_layers.ChargesLayer import ChargesLayer
from app.api.helpers.db import save_to_db, safe_query, safe_query_without_soft_deleted_entries
from app.api.helpers.errors import BadRequestError
from app.api.helpers.exceptions import ForbiddenException, UnprocessableEntity, ConflictException
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.mail import send_order_cancel_email
from app.api.helpers.notification import send_notif_to_attendees, send_notif_ticket_purchase_organizer, \
    send_notif_ticket_cancel
from app.api.helpers.order import delete_related_attendees_for_order, set_expiry_for_order, \
    create_pdf_tickets_for_holder, create_onsite_attendees_for_order
from app.api.helpers.payment import PayPalPaymentsManager
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.query import event_query
from app.api.helpers.ticketing import TicketingManager
from app.api.helpers.utilities import dasherize, require_relationship
from app.api.schema.orders import OrderSchema
from app.models import db
from app.models.discount_code import DiscountCode, TICKET
from app.models.order import Order, OrderTicket, get_updatable_fields
from app.models.ticket_holder import TicketHolder
from app.models.user import User

order_misc_routes = Blueprint('order_misc', __name__, url_prefix='/v1')


class OrdersListPost(ResourceList):
    """
    OrderListPost class for OrderSchema
    """

    def before_post(self, args, kwargs, data=None):
        """
        before post method to check for required relationships and permissions
        :param args:
        :param kwargs:
        :param data:
        :return:
        """
        require_relationship(['event'], data)

        # Create on site attendees.
        if request.args.get('onsite', False):
            create_onsite_attendees_for_order(data)
        elif data.get('on_site_tickets'):
            del data['on_site_tickets']
        require_relationship(['ticket_holders'], data)

        # Ensuring that default status is always pending, unless the user is event co-organizer
        if not has_access('is_coorganizer', event_id=data['event']):
            data['status'] = 'pending'

    def before_create_object(self, data, view_kwargs):
        """
        before create object method for OrderListPost Class
        :param data:
        :param view_kwargs:
        :return:
        """
        for ticket_holder in data['ticket_holders']:
            # Ensuring that the attendee exists and doesn't have an associated order.
            try:
                ticket_holder_object = self.session.query(TicketHolder).filter_by(id=int(ticket_holder),
                                                                                  deleted_at=None).one()
                if ticket_holder_object.order_id:
                    raise ConflictException({'pointer': '/data/relationships/attendees'},
                                            "Order already exists for attendee with id {}".format(str(ticket_holder)))
            except NoResultFound:
                raise ConflictException({'pointer': '/data/relationships/attendees'},
                                        "Attendee with id {} does not exists".format(str(ticket_holder)))

        if data.get('cancel_note'):
            del data['cancel_note']

        if data.get('payment_mode') != 'free' and not data.get('amount'):
            raise ConflictException({'pointer': '/data/attributes/amount'},
                                    "Amount cannot be null for a paid order")

        # Apply discount only if the user is not event admin
        if data.get('discount') and not has_access('is_coorganizer', event_id=data['event']):
            discount_code = safe_query_without_soft_deleted_entries(self, DiscountCode, 'id', data['discount'],
                                                                    'discount_code_id')
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
        :param order: Object created from mashmallow_jsonapi
        :param data:
        :param view_kwargs:
        :return:
        """
        order_tickets = {}
        for holder in order.ticket_holders:
            save_to_db(holder)
            if not order_tickets.get(holder.ticket_id):
                order_tickets[holder.ticket_id] = 1
            else:
                order_tickets[holder.ticket_id] += 1

        order.user = current_user

        # create pdf tickets.
        create_pdf_tickets_for_holder(order)

        for ticket in order_tickets:
            od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
            save_to_db(od)

        order.quantity = order.tickets_count
        save_to_db(order)
#         if not has_access('is_coorganizer', event_id=data['event']):
#             TicketingManager.calculate_update_amount(order)

        # send e-mail and notifications if the order status is completed
        if order.status == 'completed':
            send_email_to_attendees(order, current_user.id)
            send_notif_to_attendees(order, current_user.id)

            order_url = make_frontend_url(path='/orders/{identifier}'.format(identifier=order.identifier))
            for organizer in order.event.organizers:
                send_notif_ticket_purchase_organizer(organizer, order.invoice_number, order_url, order.event.name,
                                                     order.identifier)

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
        if kwargs.get('event_id') and not has_access('is_coorganizer', event_id=kwargs['event_id']):
            raise ForbiddenException({'source': ''}, "Co-Organizer Access Required")

    def query(self, view_kwargs):
        query_ = self.session.query(Order)
        if view_kwargs.get('user_id'):
            # orders under a user
            user = safe_query(self, User, 'id', view_kwargs['user_id'], 'user_id')
            if not has_access('is_user_itself', user_id=user.id):
                raise ForbiddenException({'source': ''}, 'Access Forbidden')
            query_ = query_.join(User, User.id == Order.user_id).filter(User.id == user.id)
        else:
            # orders under an event
            query_ = event_query(self, query_, view_kwargs)

        # expire the pending orders if the time limit is over.
        orders = query_.all()
        for order in orders:
            set_expiry_for_order(order)

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
            view_kwargs['id'] = attendee.order.id
        if view_kwargs.get('order_identifier'):
            order = safe_query(self, Order, 'identifier', view_kwargs['order_identifier'], 'order_identifier')
            view_kwargs['id'] = order.id
        elif view_kwargs.get('id'):
            order = safe_query(self, Order, 'id', view_kwargs['id'], 'id')

        if not has_access('is_coorganizer_or_user_itself', event_id=order.event_id, user_id=order.user_id):
            return ForbiddenException({'source': ''}, 'You can only access your orders or your event\'s orders')

        # expire the pending order if time limit is over.
        set_expiry_for_order(order)

    def before_update_object(self, order, data, view_kwargs):
        """
        before update object method of order details
        1. admin can update all the fields.
        2. event organizer
            a. own orders: he/she can update selected fields.
            b. other's orders: can only update the status that too when the order mode is free. No refund system.
        3. order user can update selected fields of his/her order when the status is pending.
        The selected fields mentioned above can be taken from get_updatable_fields method from order model.
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        if (not has_access('is_coorganizer', event_id=order.event_id)) and (not current_user.id == order.user_id):
            raise ForbiddenException({'pointer': ''}, "Access Forbidden")

        if has_access('is_coorganizer_but_not_admin', event_id=order.event_id):
            if current_user.id == order.user_id:
                # Order created from the tickets tab.
                for element in data:
                    if data[element] and data[element]\
                            != getattr(order, element, None) and element not in get_updatable_fields():
                        raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                 "You cannot update {} of an order".format(element))

            else:
                # Order created from the public pages.
                for element in data:
                    if data[element] and data[element] != getattr(order, element, None):
                        if element != 'status':
                            raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                     "You cannot update {} of an order".format(element))
                        elif element == 'status' and order.amount and order.status == 'completed':
                            # Since we don't have a refund system.
                            raise ForbiddenException({'pointer': 'data/status'},
                                                     "You cannot update the status of a completed paid order")
                        elif element == 'status' and order.status == 'cancelled':
                            # Since the tickets have been unlocked and we can't revert it.
                            raise ForbiddenException({'pointer': 'data/status'},
                                                     "You cannot update the status of a cancelled order")

        elif current_user.id == order.user_id:
            if order.status != 'pending':
                raise ForbiddenException({'pointer': ''},
                                         "You cannot update a non-pending order")
            else:
                for element in data:
                    if element == 'is_billing_enabled' and order.status == 'completed' and data[element]\
                            and data[element] != getattr(order, element, None):
                        raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                 "You cannot update {} of a completed order".format(element))
                    elif data[element] and data[element]\
                            != getattr(order, element, None) and element not in get_updatable_fields():
                        raise ForbiddenException({'pointer': 'data/{}'.format(element)},
                                                 "You cannot update {} of an order".format(element))

        if has_access('is_organizer', event_id=order.event_id) and 'order_notes' in data:
            if order.order_notes and data['order_notes'] not in order.order_notes.split(","):
                data['order_notes'] = '{},{}'.format(order.order_notes, data['order_notes'])

    def after_update_object(self, order, data, view_kwargs):
        """
        :param order:
        :param data:
        :param view_kwargs:
        :return:
        """
        # create pdf tickets.
        create_pdf_tickets_for_holder(order)

        if order.status == 'cancelled':
            send_order_cancel_email(order)
            send_notif_ticket_cancel(order)

            # delete the attendees so that the tickets are unlocked.
            delete_related_attendees_for_order(order)

    def before_delete_object(self, order, view_kwargs):
        """
        method to check for proper permissions for deleting
        :param order:
        :param view_kwargs:
        :return:
        """
        if not has_access('is_coorganizer', event_id=order.event.id):
            raise ForbiddenException({'source': ''}, 'Access Forbidden')
        elif order.amount and order.amount > 0 and (order.status == 'completed' or order.status == 'placed'):
            raise ConflictException({'source': ''}, 'You cannot delete a placed/completed paid order.')

    # This is to ensure that the permissions manager runs and hence changes the kwarg from order identifier to id.
    decorators = (jwt_required, api.has_permission(
        'auth_required', methods="PATCH,DELETE", model=Order),)
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
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

    def before_get(self, args, kwargs):
        """
        before get method to get the resource id for fetching details
        :param view_kwargs:
        :return:
        """
        if kwargs.get('order_identifier'):
            order = safe_query(db, Order, 'identifier', kwargs['order_identifier'], 'order_identifier')
            kwargs['id'] = order.id
        elif kwargs.get('id'):
            order = safe_query(db, Order, 'id', kwargs['id'], 'id')

        if not has_access('is_coorganizer', event_id=order.event_id, user_id=order.user_id):
            return ForbiddenException({'source': ''}, 'You can only access your orders or your event\'s orders')

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
        self_view_kwargs = {'order_identifier': '<id>'}

    id = fields.Str(dump_only=True)
    stripe = fields.Str(load_only=True, allow_none=True)
    paypal_payer_id = fields.Str(load_only=True, allow_none=True)
    paypal_payment_id = fields.Str(load_only=True, allow_none=True)
    status = fields.Boolean(dump_only=True)
    message = fields.Str(dump_only=True)


class ChargeList(ResourceList):
    """
    ChargeList ResourceList for ChargesLayer class
    """
    methods = ['POST', ]
    schema = ChargeSchema

    data_layer = {
        'class': ChargesLayer,
        'session': db.session,
        'model': Order
    }

    decorators = (jwt_required,)


@order_misc_routes.route('/orders/<string:order_identifier>/create-paypal-payment', methods=['POST'])
@jwt_required
def create_paypal_payment(order_identifier):
    """
    Create a paypal payment.
    :return: The payment id of the created payment.
    """
    try:
        return_url = request.json['data']['attributes']['return-url']
        cancel_url = request.json['data']['attributes']['cancel-url']
    except TypeError:
        return BadRequestError({'source': ''}, 'Bad Request Error').respond()

    order = safe_query(db, Order, 'identifier', order_identifier, 'identifier')
    status, response = PayPalPaymentsManager.create_payment(order, return_url, cancel_url)

    if status:
        return jsonify(status=True, payment_id=response)
    else:
        return jsonify(status=False, error=response)

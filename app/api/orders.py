from datetime import datetime

from flask import request
from flask_rest_jsonapi import ResourceDetail, ResourceList, ResourceRelationship
from marshmallow_jsonapi.flask import Schema, Relationship
from marshmallow_jsonapi import fields
from marshmallow import post_dump, validates_schema, validate
from flask_jwt import current_identity as current_user

from app.api.bootstrap import api
from app.api.data_layers.ChargesLayer import ChargesLayer
from app.api.helpers.db import save_to_db, safe_query
from app.api.helpers.exceptions import ForbiddenException, UnprocessableEntity
from app.api.helpers.payment import PayPalPaymentsManager
from app.api.helpers.ticketing import TicketingManager
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.api.helpers.utilities import dasherize, require_relationship
from app.models import db
from app.models.discount_code import DiscountCode, TICKET
from app.models.order import Order, OrderTicket


class OrderSchema(Schema):
    class Meta:
        type_ = 'order'
        self_view = 'v1.order_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    @post_dump
    def generate_payment_url(self, data):
        if 'POST' in request.method or ('GET' in request.method and 'regenerate' in request.args) and 'completed' != \
           data["status"]:
            if data['payment_mode'] == 'stripe':
                data['payment_url'] = 'stripe://payment'
            elif data['payment_mode'] == 'paypal':
                order = Order.query.filter_by(id=data['id']).first()
                data['payment_url'] = PayPalPaymentsManager.get_checkout_url(order)
        return data

    @validates_schema
    def initial_values(self, data):
        if data.get('payment_mode') is None and 'POST' in request.method:
            data['payment_mode'] = 'free'
        return data

    id = fields.Str(dump_only=True)
    identifier = fields.Str(dump_only=True)
    amount = fields.Float(validate=lambda n: n > 0)
    address = fields.Str()
    city = fields.Str()
    state = fields.Str(db.String)
    country = fields.Str(required=True)
    zipcode = fields.Str()
    completed_at = fields.DateTime(dump_only=True)
    transaction_id = fields.Str(dump_only=True)
    payment_mode = fields.Str()
    paid_via = fields.Str(dump_only=True)
    brand = fields.Str(dump_only=True)
    exp_month = fields.Str(dump_only=True)
    exp_year = fields.Str(dump_only=True)
    last4 = fields.Str(dump_only=True)
    status = fields.Str(validate=validate.OneOf(choices=["pending", "cancelled", "confirmed", "deleted"]))
    discount_code_id = fields.Str()
    payment_url = fields.Str(dump_only=True)

    attendees = Relationship(attribute='ticket_holders',
                             self_view='v1.order_attendee',
                             self_view_kwargs={'identifier': '<identifier>'},
                             related_view='v1.attendee_list',
                             related_view_kwargs={'order_id': '<id>'},
                             schema='AttendeeSchema',
                             many=True,
                             type_='attendee')

    tickets = Relationship(self_view='v1.order_ticket',
                           self_view_kwargs={'identifier': '<identifier>'},
                           related_view='v1.ticket_list',
                           related_view_kwargs={'order_id': '<id>'},
                           schema='TicketSchema',
                           many=True,
                           type_="ticket")

    user = Relationship(self_view='v1.order_user',
                        self_view_kwargs={'identifier': '<identifier>'},
                        related_view='v1.user_detail',
                        related_view_kwargs={'id': '<user_id>'},
                        schema='UserSchema',
                        type_="user")

    event = Relationship(self_view='v1.order_event',
                         self_view_kwargs={'identifier': '<identifier>'},
                         related_view='v1.event_detail',
                         related_view_kwargs={'id': '<event_id>'},
                         schema='EventSchema',
                         type_="event")

    marketer = Relationship(self_view='v1.order_marketer',
                            self_view_kwargs={'identifier': '<identifier>'},
                            related_view='v1.user_detail',
                            related_view_kwargs={'id': '<marketer_id>'},
                            schema='UserSchema',
                            type_="user")

    discount_code = Relationship(self_view='v1.order_discount',
                                 self_view_kwargs={'identifier': '<identifier>'},
                                 related_view='v1.discount_code_detail',
                                 related_view_kwargs={'id': '<discount_code_id>'},
                                 schema='DiscountCodeSchema',
                                 type_="discount-code")


class OrdersListPost(ResourceList):
    def before_post(self, args, kwargs, data=None):
        require_relationship(['event'], data)
        if not has_access('is_coorganizer', event_id=data['event']):
            data['status'] = 'pending'

    def before_create_object(self, data, view_kwargs):
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
        order_tickets = {}
        for holder in order.ticket_holders:
            if order_tickets.get(holder.ticket_id) is None:
                order_tickets[holder.ticket_id] = 1
            else:
                order_tickets[holder.ticket_id] += 1
        for ticket in order_tickets:
            od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
            save_to_db(od)
        order.quantity = order.get_tickets_count()
        save_to_db(order)
        if not has_access('is_coorganizer', **view_kwargs):
            TicketingManager.calculate_update_amount(order)

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
    def before_get(self, args, kwargs):
        if kwargs.get('event_id') is None:
            if 'GET' in request.method and has_access('is_admin'):
                pass
            else:
                raise ForbiddenException({'source': ''}, "Admin Access Required")
        elif not has_access('is_coorganizer', event_id=kwargs['event_id']):
            raise ForbiddenException({'source': ''}, "Co-Organizer Access Required")

    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order}


class OrderDetail(ResourceDetail):
    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            order = safe_query(self, Order, 'identifier', view_kwargs['identifier'], 'order_identifier')
            view_kwargs['id'] = order.id

    def before_update_object(self, order, data, view_kwargs):
        if data.get('status'):
            if has_access('is_coorganizer', event_id=order.event.id):
                pass
            else:
                raise ForbiddenException({'pointer': 'data/status'},
                                         "To update status minimum Co-organizer access required")

    decorators = (api.has_permission('is_coorganizer', fetch="event_id", fetch_as="event_id", model=Order),)

    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order,
                  'methods': {'before_update_object': before_update_object}}


class OrderRelationship(ResourceRelationship):
    decorators = (jwt_required,)
    schema = OrderSchema
    data_layer = {'session': db.session,
                  'model': Order}


class ChargeSchema(Schema):
    class Meta:
        type_ = 'charge'
        inflect = dasherize
        self_view = 'v1.charge_list'
        self_view_kwargs = {'id': '<id>'}

    id = fields.Str(dump_only=True)
    stripe = fields.Str(allow_none=True)


class ChargeList(ResourceList):
    methods = ['POST', ]
    schema = ChargeSchema

    data_layer = {
        'class': ChargesLayer,
        'session': db.session
    }

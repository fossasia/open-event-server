from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import func

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.order import Order, OrderTicket
from app.models.user import User


def sales_per_marketer_and_discount_by_status(status):
    return (
        db.session.query(
            Event.id.label('event_id'),
            DiscountCode.id.label('discount_code_id'),
            User.id.label('marketer_id'),
            func.sum(Order.amount).label(status + '_sales'),
            func.sum(OrderTicket.quantity).label(status + '_tickets'),
        )
        .filter(Event.id == Order.event_id)
        .filter(Order.marketer_id == User.id)
        .filter(Order.discount_code_id == DiscountCode.id)
        .filter(Order.status == status)
        .group_by(Event)
        .group_by(DiscountCode)
        .group_by(User)
        .group_by(Order.status)
        .cte()
    )


class AdminSalesDiscountedSchema(Schema):
    """
    Discounted sales by event

    Provides
        Event name,
        discount code,
        marketer mail,
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-discounted'
        self_view = 'v1.admin_sales_discounted'
        inflect = dasherize

    id = fields.String()
    code = fields.String()
    email = fields.String()
    event_name = fields.String()
    payment_currency = fields.String()
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        res = {'placed': {}, 'completed': {}, 'pending': {}}
        res['placed']['sales_total'] = obj.placed_sales or 0
        res['placed']['ticket_count'] = obj.placed_tickets or 0
        res['completed']['sales_total'] = obj.completed_sales or 0
        res['completed']['ticket_count'] = obj.completed_tickets or 0
        res['pending']['sales_total'] = obj.pending_sales or 0
        res['pending']['ticket_count'] = obj.pending_tickets or 0

        return res


class AdminSalesDiscountedList(ResourceList):
    """
    Resource for sales by marketer. Joins event marketer and orders and
    subsequently accumulates sales by status
    """

    def query(self, _):
        pending = sales_per_marketer_and_discount_by_status('pending')
        completed = sales_per_marketer_and_discount_by_status('completed')
        placed = sales_per_marketer_and_discount_by_status('placed')

        discounts = (
            self.session.query(
                Event.id.label('event_id'),
                Event.name.label('event_name'),
                DiscountCode.id.label('discount_code_id'),
                DiscountCode.code.label('code'),
                User.id.label('marketer_id'),
                User.email.label('email'),
            )
            .filter(Event.id == Order.event_id)
            .filter(Order.marketer_id == User.id)
            .filter(Order.discount_code_id == DiscountCode.id)
            .cte()
        )

        return (
            self.session.query(discounts, pending, completed, placed)
            .outerjoin(
                pending,
                (pending.c.event_id == discounts.c.event_id)
                & (pending.c.discount_code_id == discounts.c.discount_code_id)
                & (pending.c.marketer_id == discounts.c.marketer_id),
            )
            .outerjoin(
                completed,
                (completed.c.event_id == discounts.c.event_id)
                & (completed.c.discount_code_id == discounts.c.discount_code_id)
                & (completed.c.marketer_id == discounts.c.marketer_id),
            )
            .outerjoin(
                placed,
                (placed.c.event_id == discounts.c.event_id)
                & (placed.c.discount_code_id == discounts.c.discount_code_id)
                & (placed.c.marketer_id == discounts.c.marketer_id),
            )
        )

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesDiscountedSchema
    data_layer = {'model': Event, 'session': db.session, 'methods': {'query': query}}

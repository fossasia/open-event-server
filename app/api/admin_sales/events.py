from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.models.order import Order


def summary(orders, status):
    """
    Groups orders by status and returns the total sales and ticket count as a
    dictionary
    """
    return {
        'sales_total': sum([o.amount for o in orders if o.status == status]),
        'ticket_count': len([o for o in orders if o.status == status])
    }


class AdminSalesByEventsSchema(Schema):
    """
    Sales summarized by event

    Provides
        event(name),
        date,
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-by-events'
        self_view = 'v1.admin_sales_by_events'

    id = fields.String()
    name = fields.String()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    pending = fields.Method('sales')

    @staticmethod
    def sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        status_codes = ['placed', 'completed', 'pending']
        return {s: summary(obj.orders, s) for s in status_codes}


class AdminSalesByEventsList(ResourceList):
    """
    Resource for sales by events. Joins events with orders and subsequently
    accumulates by status
    """

    def query(self, _):
        return self.session.query(Event).join(Order)

    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    schema = AdminSalesByEventsSchema
    data_layer = {
        'model': Event,
        'session': db.session,
        'methods': {
            'query': query
        }
    }

from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.helpers.utilities import dasherize
from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.models.order import Order, OrderTicket

from app.api.admin_sales.utils import summary


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
        inflect = dasherize

    id = fields.String()
    name = fields.String()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    payment_currency = fields.String()
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        return summary(obj.orders)


class AdminSalesByEventsList(ResourceList):
    """
    Resource for sales by events. Joins events with orders and subsequently
    accumulates by status
    """

    def query(self, _):
        return self.session.query(Event).outerjoin(Order).outerjoin(OrderTicket)

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

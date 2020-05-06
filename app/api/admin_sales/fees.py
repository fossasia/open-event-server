from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event


class AdminSalesFeesSchema(Schema):
    """
    Sales fees and revenue for all events
    """

    class Meta:
        type_ = 'admin-sales-fees'
        self_view = 'v1.admin_sales_fees'
        inflect = dasherize

    id = fields.String()
    name = fields.String()
    payment_currency = fields.String()
    fee_percentage = fields.Float(attribute='fee')
    maximum_fee = fields.Float(attribute='maximum_fee')
    revenue = fields.Method('calc_revenue')
    ticket_count = fields.Method('calc_ticket_count')
    event_date = fields.Method('get_event_date')

    @staticmethod
    def calc_ticket_count(obj):
        """Count all tickets in all orders of this event"""
        return sum(o.tickets_count for o in obj.orders if o.status == 'completed')

    @staticmethod
    def calc_revenue(obj):
        """Returns total revenues of all completed orders for the given event"""
        return sum(o.get_revenue() for o in obj.orders if o.status == 'completed')

    @staticmethod
    def get_event_date(obj):
        return obj.starts_at.isoformat()


class AdminSalesFeesList(ResourceList):
    """
    Resource for sales fees and revenue
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesFeesSchema
    data_layer = {'model': Event, 'session': db.session}

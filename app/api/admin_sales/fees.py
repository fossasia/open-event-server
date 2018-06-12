from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.models import db
from app.models.order import Order, OrderTicket
from app.models.user import User
from app.models.event import Event


class AdminSalesFeesSchema(Schema):
    """
    Sales fees and revenue for all events
    """

    class Meta:
        type_ = 'admin-sales-fees'
        self_view = 'v1.admin_sales_fees'

    id = fields.String()
    name = fields.String()
    fee = fields.Float()
    revenue = fields.Method('calc_revenue')

    @staticmethod
    def calc_revenue(obj):
        "Returns total revenues of all completed orders for the given event"
        return sum(
            [o.get_revenue() for o in obj.orders if o.status == 'completed'])


class AdminSalesFeesList(ResourceList):
    """
    Resource for sales fees and revenue
    """

    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    schema = AdminSalesFeesSchema
    data_layer = {'model': Event, 'session': db.session}

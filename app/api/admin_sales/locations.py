from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList

from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.models.order import Order

from app.api.admin_sales.utils import summary


class AdminSalesByLocationSchema(Schema):
    """
    Sales summarized by location

    Provides
        location (first name and last name),
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-by-location'
        self_view = 'v1.admin_sales_by_location'

    id = fields.String()
    location_name = fields.String()
    # sales = fields.Method('calc_sales')

    # @staticmethod
    # def calc_sales(obj):
    #     """
    #     Returns sales (dictionary with total sales and ticket count) for
    #     placed, completed and pending orders
    #     """
    #     status_codes = ['placed', 'completed', 'pending']
    #     return {s: summary(obj.orders, s) for s in status_codes}


class AdminSalesByLocationList(ResourceList):
    """
    Resource for sales by location. Joins events and orders
    and subsequently accumulates sales by status
    """

    def query(self, _):
        return self.session.execute("select * from events")
    # .query(Event.id, Event.location_name).outerjoin(Order)

    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    schema = AdminSalesByLocationSchema
    data_layer = {
        'model': Event,
        'session': db.session,
        'methods': {
            'query': query
        }
    }

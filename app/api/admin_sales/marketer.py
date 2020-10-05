from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.admin_sales.utils import summary
from app.api.bootstrap import api
from app.models import db
from app.models.order import Order, OrderTicket
from app.models.user import User


class AdminSalesByMarketerSchema(Schema):
    """
    Sales summarized by marketer

    Provides
        marketer name,
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-by-marketer'
        self_view = 'v1.admin_sales_by_marketer'

    id = fields.String()
    fullname = fields.String()
    email = fields.String()
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        return summary(obj)


class AdminSalesByMarketerList(ResourceList):
    """
    Resource for sales by marketer. Joins event marketer and orders and
    subsequently accumulates sales by status
    """

    def query(self, _):
        return (
            self.session.query(User)
            .join(Order, Order.marketer_id == User.id)
            .outerjoin(OrderTicket)
        )

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesByMarketerSchema
    data_layer = {'model': User, 'session': db.session, 'methods': {'query': query}}

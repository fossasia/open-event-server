from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.admin_sales.utils import summary
from app.api.bootstrap import api
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event


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
    identifier = fields.String()
    name = fields.String()
    created_at = fields.DateTime()
    deleted_at = fields.DateTime()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    payment_currency = fields.String()
    payment_country = fields.String()
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        return summary(obj)


class AdminSalesByEventsList(ResourceList):
    """
    Resource for sales by events. Joins events with orders and subsequently
    accumulates by status
    """

    def query(self, _):
        return Event.query

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesByEventsSchema
    data_layer = {'model': Event, 'session': db.session, 'methods': {'query': query}}

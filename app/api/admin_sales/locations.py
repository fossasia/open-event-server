from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from flask_rest_jsonapi import ResourceList
from sqlalchemy import func
from app.api.helpers.utilities import dasherize

from app.api.bootstrap import api
from app.models import db
from app.models.event import Event
from app.models.order import Order, OrderTicket


def sales_per_location_by_status(status):
    return db.session.query(
        Event.location_name.label('location'),
        func.sum(Order.amount).label(status + '_sales'),
        func.sum(OrderTicket.quantity).label(status + '_tickets')) \
                     .outerjoin(Order) \
                     .outerjoin(OrderTicket) \
                     .filter(Event.id == Order.event_id) \
                     .filter(Order.status == status) \
                     .group_by(Event.location_name, Order.status) \
                     .cte()


class AdminSalesByLocationSchema(Schema):
    """
    Sales summarized by location

    Provides
        location name,
        count of tickets and total sales for orders grouped by status
    """

    class Meta:
        type_ = 'admin-sales-by-location'
        self_view = 'v1.admin_sales_by_location'
        inflect = dasherize

    id = fields.String()
    location_name = fields.String()
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


class AdminSalesByLocationList(ResourceList):
    """
    Resource for sales by location. Joins event locations and orders and
    subsequently accumulates sales by status
    """

    def query(self, _):
        locations = self.session.query(
            Event.location_name,
            Event.location_name.label('id')) \
                .group_by(Event.location_name) \
                .filter(Event.location_name.isnot(None)) \
                .cte()

        pending = sales_per_location_by_status('pending')
        completed = sales_per_location_by_status('completed')
        placed = sales_per_location_by_status('placed')

        return self.session.query(locations, pending, completed, placed) \
                           .outerjoin(pending, pending.c.location == locations.c.location_name) \
                           .outerjoin(completed, completed.c.location == locations.c.location_name) \
                           .outerjoin(placed, placed.c.location == locations.c.location_name)

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

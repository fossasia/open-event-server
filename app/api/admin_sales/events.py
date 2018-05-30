from app.api.bootstrap import api
from app.models import db
from app.models.order import Order
from app.models.event import Event

from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema


def summary(orders, status):
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

    def sales(self, obj):
        status_codes = ['placed', 'completed', 'pending']
        return {s: summary(obj.orders, s) for s in status_codes}


class AdminSalesByEventsList(ResourceList):
    def query(self, view_kwargs):
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

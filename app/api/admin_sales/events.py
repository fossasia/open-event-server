from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.admin_sales.utils import summary
from app.api.bootstrap import api
from app.api.helpers.db import save_to_db
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
    total_sales = fields.Integer()
    identifier = fields.String()
    name = fields.String()
    created_at = fields.DateTime()
    deleted_at = fields.DateTime()
    starts_at = fields.DateTime()
    ends_at = fields.DateTime()
    payment_currency = fields.String()
    payment_country = fields.String()
    type = fields.Method('event_type')
    owner = fields.Method('event_owner')
    owner_id = fields.Method('event_owner_id')
    sales = fields.Method('calc_sales')

    @staticmethod
    def calc_sales(obj):
        """
        Returns sales (dictionary with total sales and ticket count) for
        placed, completed and pending orders
        """
        return summary(obj)

    def event_owner(self, obj):
        return str(obj.owner.email)

    def event_owner_id(self, obj):
        return obj.owner.id

    def event_type(self, obj):
        t = 'To be announced'
        if obj.online:
            if obj.location_name:
                t = 'Hybrid'
            else:
                t = 'Online'
        elif obj.location_name:
            t = 'Venue'
        return str(t)


class AdminSalesByEventsList(ResourceList):
    """
    Resource for sales by events. Joins events with orders and subsequently
    accumulates by status
    """

    def query(self, _):
        return Event.query

    def before_get(self, args, kwargs):
        events = Event.query.all()
        for event in events:
            event.total_sales = summary(event, return_total_sales=True)
            save_to_db(event)

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesByEventsSchema
    data_layer = {
        'model': Event,
        'session': db.session,
        'methods': {'query': query, 'before_get': before_get},
    }

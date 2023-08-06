from flask_rest_jsonapi import ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema

from app.api.admin_sales.utils import summary_by_id
from app.api.bootstrap import api
from app.api.helpers.db import save_bulk_to_db
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
    completed_order_sales = fields.Integer(dump_only=True)
    placed_order_sales = fields.Integer(dump_only=True)
    pending_order_sales = fields.Integer(dump_only=True)
    completed_order_tickets = fields.Integer(dump_only=True)
    placed_order_tickets = fields.Integer(dump_only=True)
    pending_order_tickets = fields.Integer(dump_only=True)
    type = fields.Method('event_type')
    owner = fields.Method('event_owner')
    owner_id = fields.Method('event_owner_id')

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

    def after_get(self, res):
        """following the get event, compute the price"""
        if 'data' in res:
            data = res['data']
            _events_id = map(lambda x: x['id'], data)

            events = Event.query.filter(Event.id.in_(_events_id)).all()
            for event in events:
                sales = summary_by_id(event.id)

                event.completed_order_sales = sales['completed']['sales_total']
                event.placed_order_sales = sales['placed']['sales_total']
                event.pending_order_sales = sales['pending']['sales_total']
                event.completed_order_tickets = sales['completed']['ticket_count']
                event.placed_order_tickets = sales['placed']['ticket_count']
                event.pending_order_tickets = sales['pending']['ticket_count']
                res_event_json = next((x for x in data if x['id'] == str(event.id)), None)
                if res_event_json is not None:
                    res_event_json['attributes']['completed-order-sales'] = sales[
                        'completed'
                    ]['sales_total']
                    res_event_json['attributes']['placed-order-sales'] = sales['placed'][
                        'sales_total'
                    ]
                    res_event_json['attributes']['pending-order-sales'] = sales[
                        'pending'
                    ]['sales_total']
                    res_event_json['attributes']['completed-order-tickets'] = sales[
                        'completed'
                    ]['ticket_count']
                    res_event_json['attributes']['placed-order-tickets'] = sales[
                        'placed'
                    ]['ticket_count']
                    res_event_json['attributes']['pending-order-tickets'] = sales[
                        'pending'
                    ]['ticket_count']
            save_bulk_to_db(events)

    methods = ['GET']
    decorators = (api.has_permission('is_admin'),)
    schema = AdminSalesByEventsSchema
    data_layer = {
        'model': Event,
        'session': db.session,
        'methods': {'query': query, 'after_get': after_get},
    }

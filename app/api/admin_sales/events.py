from app.api.bootstrap import api
from app.api.data_layers.NoModelLayer import NoModelLayer
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.order import Order, OrderTicket
from app.models.event import Event

from flask_rest_jsonapi import ResourceDetail, ResourceList
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema, Relationship


class AdminStatisticsEventSchema(Schema):
    """
    Tickets summarized by event

    Provides
        event(name),
        date,
        count of tickets and total sales for completed orders,
        count of tickets and total sales for placed orders,
        count of tickets and total sales for pending orders
    """

    class Meta:
        type_ = 'admin-sales-by-event'

    id = fields.String(dump_only=True)

    created_at = fields.DateTime()
    completed_at = fields.DateTime()

    completed = fields.Method("completed_tickets_and_sales")
    placed = fields.Method("placed_tickets_and_sales")
    pending = fields.Method("pending_tickets_and_sales")

    def completed_tickets_and_sales(self, obj):
        return # TODO self.session.query(Event) #.filter_by(event_id=obj.id)

    def placed_tickets_and_sales(self, obj):
        return self.session.query(OrderTicket)

    def pending_tickets_and_sales(self, obj):
        return 42


class AdminSalesByEvents(ResourceList):
    schema = AdminStatisticsEventSchema
    methods = ['GET']
    decorators = (api.has_permission('is_admin'), )
    data_layer = {'model': Event, 'session': db.session}

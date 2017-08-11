from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi.flask import Schema
from marshmallow_jsonapi import fields
from sqlalchemy import func

from app.api.helpers.utilities import dasherize
from app.api.helpers.db import safe_query
from app.api.bootstrap import api
from app.models import db
from app.models.order import Order, OrderTicket
from app.models.event import Event
from app.api.helpers.db import get_count


class TicketStatisticsEventSchema(Schema):
    """
    Api schema for general statistics of event
    """

    class Meta:
        """
        Meta class
        """
        type_ = 'ticket-statistics-event'
        self_view = 'v1.ticket_statistics_event_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str()
    identifier = fields.Str()
    tickets = fields.Method("tickets_count")
    orders = fields.Method("orders_count")
    sales = fields.Method("sales_count")

    def tickets_count(self, obj):
        obj_id = obj.id
        total = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id).scalar()
        draft = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id, Order.status == 'draft').scalar()
        cancelled = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id, Order.status == 'cancelled').scalar()
        pending = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id, Order.status == 'pending').scalar()
        expired = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id, Order.status == 'expired').scalar()
        placed = db.session.query(func.sum(OrderTicket.quantity.label('sum'))).join(Order.order_tickets).filter(
            Order.event_id == obj_id, Order.status == 'placed').scalar()
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0
        }
        return result

    def orders_count(self, obj):
        obj_id = obj.id
        total = get_count(db.session.query(Order).filter(Order.event_id == obj_id))
        draft = get_count(db.session.query(Order).filter(Order.event_id == obj_id, Order.status == 'draft'))
        cancelled = get_count(db.session.query(Order).filter(Order.event_id == obj_id, Order.status == 'cancelled'))
        pending = get_count(db.session.query(Order).filter(Order.event_id == obj_id, Order.status == 'pending'))
        expired = get_count(db.session.query(Order).filter(Order.event_id == obj_id, Order.status == 'expired'))
        placed = get_count(db.session.query(Order).filter(Order.event_id == obj_id, Order.status == 'placed'))
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0
        }
        return result

    def sales_count(self, obj):
        obj_id = obj.id
        total = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id).scalar()
        draft = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id,
                                                                             Order.status == 'draft').scalar()
        cancelled = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id,
                                                                                 Order.status == 'cancelled').scalar()
        pending = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id,
                                                                               Order.status == 'pending').scalar()
        expired = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id,
                                                                               Order.status == 'expired').scalar()
        placed = db.session.query(func.sum(Order.amount.label('sum'))).filter(Order.event_id == obj_id,
                                                                              Order.status == 'placed').scalar()
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0
        }
        return result


class TicketStatisticsEventDetail(ResourceDetail):
    """
    Event statistics detail by id
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query(self, Event, 'identifier', view_kwargs['identifier'], 'identifier')
            view_kwargs['id'] = event.id

    methods = ['GET']
    decorators = (api.has_permission('is_coorganizer', fetch="id", fetch_as="event_id", model=Event),)
    schema = TicketStatisticsEventSchema
    data_layer = {'session': db.session,
                  'model': Event,
                  'methods': {
                      'before_get_object': before_get_object
                  }}

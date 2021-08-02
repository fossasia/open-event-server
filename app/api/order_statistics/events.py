from flask_rest_jsonapi import ResourceDetail
from marshmallow_jsonapi import fields
from marshmallow_jsonapi.flask import Schema
from sqlalchemy import func

from app.api.bootstrap import api
from app.api.helpers.db import get_count, safe_query_kwargs
from app.api.helpers.utilities import dasherize
from app.models import db
from app.models.event import Event
from app.models.order import Order, OrderTicket
from app.models.ticket import Ticket


class OrderStatisticsEventSchema(Schema):
    """
    Api schema for general statistics of event
    """

    class Meta:
        """
        Meta class
        """

        type_ = 'order-statistics-event'
        self_view = 'v1.order_statistics_event_detail'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str()
    identifier = fields.Str()
    tickets = fields.Method("tickets_count")
    orders = fields.Method("orders_count")
    sales = fields.Method("sales_count")

    def tickets_count(self, obj):
        obj_id = obj.id
        total = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id)
            .scalar()
        )
        draft = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'draft')
            .scalar()
        )
        cancelled = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'cancelled')
            .scalar()
        )
        pending = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'pending')
            .scalar()
        )
        expired = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'expired')
            .scalar()
        )
        placed = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'placed')
            .scalar()
        )
        completed = (
            db.session.query(func.sum(OrderTicket.quantity.label('sum')))
            .join(Order.order_tickets)
            .filter(Order.event_id == obj_id, Order.status == 'completed')
            .scalar()
        )
        max = (
            db.session.query(func.sum(Ticket.quantity.label('sum')))
            .filter(Ticket.event_id == obj_id, Ticket.deleted_at == None)
            .scalar()
        )
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0,
            'completed': completed or 0,
            'max': max or 0,
        }
        return result

    def orders_count(self, obj):
        obj_id = obj.id
        total = get_count(db.session.query(Order).filter(Order.event_id == obj_id))
        draft = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'draft'
            )
        )
        cancelled = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'cancelled'
            )
        )
        pending = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'pending'
            )
        )
        expired = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'expired'
            )
        )
        placed = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'placed'
            )
        )
        completed = get_count(
            db.session.query(Order).filter(
                Order.event_id == obj_id, Order.status == 'completed'
            )
        )
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0,
            'completed': completed or 0,
        }
        return result

    def sales_count(self, obj):
        obj_id = obj.id
        total = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id)
            .scalar()
        )
        draft = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'draft')
            .scalar()
        )
        cancelled = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'cancelled')
            .scalar()
        )
        pending = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'pending')
            .scalar()
        )
        expired = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'expired')
            .scalar()
        )
        placed = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'placed')
            .scalar()
        )
        completed = (
            db.session.query(func.sum(Order.amount.label('sum')))
            .filter(Order.event_id == obj_id, Order.status == 'completed')
            .scalar()
        )
        result = {
            'total': total or 0,
            'draft': draft or 0,
            'cancelled': cancelled or 0,
            'pending': pending or 0,
            'expired': expired or 0,
            'placed': placed or 0,
            'completed': completed or 0,
        }
        return result


class OrderStatisticsEventDetail(ResourceDetail):
    """
    Event statistics detail by id
    """

    def before_get_object(self, view_kwargs):
        if view_kwargs.get('identifier'):
            event = safe_query_kwargs(Event, view_kwargs, 'identifier', 'identifier')
            view_kwargs['id'] = event.id

    methods = ['GET']
    decorators = (
        api.has_permission(
            'is_coorganizer', fetch="id", fetch_as="event_id", model=Event
        ),
    )
    schema = OrderStatisticsEventSchema
    data_layer = {
        'session': db.session,
        'model': Event,
        'methods': {'before_get_object': before_get_object},
    }

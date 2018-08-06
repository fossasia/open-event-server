from marshmallow_jsonapi import fields
from sqlalchemy.sql import func

from app.api.helpers.utilities import dasherize
from app.api.schema.base import Schema
from app.models import db
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder
from utils.common import use_defaults


@use_defaults()
class EventOrgaSchema(Schema):
    """
    Schema for Orga Events - a minified version of Events for the Organizer App
    """

    class Meta:
        type_ = 'event-orga'
        self_view = 'v1.events_orga'
        self_view_kwargs = {'id': '<id>'}
        inflect = dasherize

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    starts_at = fields.DateTime(required=True, timezone=True)
    tickets_available = fields.Method('calc_total_tickets_count')
    tickets_sold = fields.Method('calc_tickets_sold_count')
    revenue = fields.Method('calc_revenue')
    payment_currency = fields.Str(allow_none=True)

    @staticmethod
    def calc_tickets_sold_count(obj):
        """Calculate total number of tickets sold for the event"""
        return db.session.query(Order.event_id).filter_by(event_id=obj.id, status='completed').join(TicketHolder)\
            .count()

    @staticmethod
    def calc_total_tickets_count(obj):
        """Calculate total available tickets for all types of tickets"""
        total_available = db.session.query(func.sum(Ticket.quantity)).filter_by(event_id=obj.id).scalar()
        if total_available is None:
            total_available = 0
        return total_available

    @staticmethod
    def calc_revenue(obj):
        """Returns total revenues of all completed orders for the given event"""
        revenue = db.session.query(func.sum(Order.amount)).filter_by(event_id=obj.id, status='completed').scalar()
        if revenue is None:
            revenue = 0
        return revenue

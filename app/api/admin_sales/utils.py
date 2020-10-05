"""
This module contains common sales calculations that are used throughout the
admin section
"""
from sqlalchemy import func

from app.api.helpers.db import get_count
from app.models.order import Order
from app.models.ticket_holder import TicketHolder


def status_summary(event, status):
    """
    Groups orders by status and returns the total sales and ticket count as a
    dictionary
    """
    sales = (
        Order.query.filter_by(event_id=event.id, status=status)
        .with_entities(func.sum(Order.amount))
        .scalar()
        or 0
    )
    tickets = get_count(
        TicketHolder.query.join(Order).filter(
            Order.event_id == event.id, Order.status == status
        )
    )
    return {
        'sales_total': sales,
        'ticket_count': tickets,
    }


def summary(event):
    """
    Returns sales as dictionary for all status codes
    """
    status_codes = ['placed', 'completed', 'pending']
    return {s: status_summary(event, s) for s in status_codes}

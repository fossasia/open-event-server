"""
This module contains common sales calculations that are used throughout the
admin section
"""
from sqlalchemy import func

from app.models.order import Order
from app.models.ticket_holder import TicketHolder


def status_summary(sales_summary, tickets_summary, status):
    """
    Groups orders by status and returns the total sales and ticket count as a
    dictionary
    """
    sales = 0
    tickets = 0

    for sale_status, sale in sales_summary:
        if sale_status == status:
            sales = sale

    for ticket_status, ticket in tickets_summary:
        if ticket_status == status:
            tickets = ticket

    return {
        'sales_total': sales,
        'ticket_count': tickets,
    }


def event_type(event):
    """
    Returns event type as string
    """
    t = 'To be announced'
    if event.online:
        if event.location_name:
            t = 'Hybrid'
        else:
            t = 'Online'
    elif event.location_name:
        t = 'Venue'

    return str(t)


def summary(event):
    """
    Returns sales as dictionary for all status codes
    """
    sales_summary = (
        Order.query.filter_by(event_id=event.id)
        .with_entities(Order.status, func.sum(Order.amount))
        .group_by(Order.status)
        .all()
    )
    tickets_summary = (
        TicketHolder.query.join(Order)
        .filter(Order.event_id == event.id)
        .with_entities(Order.status, func.count())
        .group_by(Order.status)
        .all()
    )
    status_codes = ['placed', 'completed', 'pending']
    return {s: status_summary(sales_summary, tickets_summary, s) for s in status_codes}

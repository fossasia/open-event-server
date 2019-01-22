"""
This module contains common sales calculations that are used throughout the
admin section
"""


def status_summary(orders, status):
    """
    Groups orders by status and returns the total sales and ticket count as a
    dictionary
    """
    return {
        'sales_total': sum([o.amount for o in orders if o.status == status]),
        'ticket_count': sum([o.tickets_count for o in orders if o.status == status])
    }


def summary(orders):
    """
    Returns sales as dictionary for all status codes
    """
    status_codes = ['placed', 'completed', 'pending']
    return {s: status_summary(orders, s) for s in status_codes}

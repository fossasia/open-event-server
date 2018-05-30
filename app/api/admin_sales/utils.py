"""
This module contains common sales calculations that are used throughout the
admin section
"""


def summary(orders, status):
    """
    Groups orders by status and returns the total sales and ticket count as a
    dictionary
    """
    return {
        'sales_total': sum([o.amount for o in orders if o.status == status]),
        'ticket_count': len([o for o in orders if o.status == status])
    }

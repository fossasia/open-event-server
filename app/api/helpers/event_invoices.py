import datetime

from app.models.event_invoice import EventInvoice


def fetch_event_invoices(invoice_status):
    """
    Helper function to fetch event invoices based on status
    """

    if invoice_status == 'due':
        event_invoices = EventInvoice.query.filter(EventInvoice.status == 'due').all()
    elif invoice_status == 'paid':
        event_invoices = EventInvoice.query.filter(EventInvoice.status == 'paid').all()
    elif invoice_status == 'upcoming':
        event_invoices = EventInvoice.query.filter(EventInvoice.status == 'upcoming').all()
    return event_invoices

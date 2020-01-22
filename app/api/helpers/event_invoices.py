import datetime

from app.models.event_invoice import EventInvoice


def fetch_event_invoices(invoice_status):
    """
    Helper function to fetch event invoices based on status
    """

    if invoice_status == 'due':
        event_invoices = EventInvoice.query.filter(
            EventInvoice.created_at + datetime.timedelta(days=30)
            <= datetime.datetime.now(),
            EventInvoice.paid_via is None,
        ).all()
    elif invoice_status == 'paid':
        event_invoices = EventInvoice.query.filter(
            EventInvoice.paid_via is not None
        ).all()
    elif invoice_status == 'upcoming':
        event_invoices = EventInvoice.query.filter(
            EventInvoice.created_at + datetime.timedelta(days=30)
            > datetime.datetime.now(),
            EventInvoice.paid_via is None,
        ).all()
    return event_invoices

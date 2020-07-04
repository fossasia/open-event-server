import datetime
from datetime import timedelta, timezone

import tests.factories.common as common
from app.api.helpers.scheduled_jobs import (
    delete_ticket_holders_no_order_id,
    event_invoices_mark_due,
    expire_initializing_tickets,
    expire_pending_tickets,
    send_monthly_event_invoice,
)
from app.models.event_invoice import EventInvoice
from app.models.ticket_holder import TicketHolder
from app.settings import get_settings
from tests.factories.attendee import AttendeeOrderSubFactory, AttendeeSubFactory
from tests.factories.event_invoice import EventInvoiceSubFactory
from tests.factories.order import OrderSubFactory
from tests.factories.ticket_fee import TicketFeesFactory


def test_delete_ticket_holder_created_currently(db):
    """Method to test not deleting ticket holders with no order id but created within expiry time"""
    attendee = AttendeeSubFactory(
        created_at=datetime.datetime.utcnow(), modified_at=datetime.datetime.utcnow(),
    )
    db.session.commit()

    attendee_id = attendee.id
    delete_ticket_holders_no_order_id()
    ticket_holder = TicketHolder.query.get(attendee_id)
    assert ticket_holder != None


def test_delete_ticket_holder_with_valid_order_id(db):
    """Method to test not deleting ticket holders with order id after expiry time"""

    attendee = AttendeeOrderSubFactory(
        created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
        modified_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
    )
    db.session.commit()

    attendee_id = attendee.id
    delete_ticket_holders_no_order_id()
    ticket_holder = TicketHolder.query.get(attendee_id)
    assert ticket_holder != None


def test_delete_ticket_holders_with_no_order_id(db):
    """Method to test deleting ticket holders with no order id after expiry time"""
    attendee = AttendeeSubFactory(created_at=common.date_)
    db.session.commit()
    attendee_id = attendee.id
    delete_ticket_holders_no_order_id()
    ticket_holder = TicketHolder.query.get(attendee_id)
    assert ticket_holder == None


def test_event_invoices_mark_due(db):
    """Method to test marking of event invoices as due"""

    event_invoice_new = EventInvoiceSubFactory(
        event__ends_at=datetime.datetime(2019, 7, 20)
    )
    event_invoice_paid = EventInvoiceSubFactory(
        status="paid", event=event_invoice_new.event
    )

    db.session.commit()

    event_invoice_new_id = event_invoice_new.id
    event_invoice_paid_id = event_invoice_paid.id

    event_invoices_mark_due()

    status_new = EventInvoice.query.get(event_invoice_new_id).status
    status_paid = EventInvoice.query.get(event_invoice_paid_id).status

    assert status_new == "due"
    assert status_paid == "paid"


def test_send_monthly_invoice(db):
    """Method to test monthly invoices"""

    TicketFeesFactory(service_fee=10.23, maximum_fee=11)
    test_order = OrderSubFactory(
        status='completed',
        event__state='published',
        completed_at=datetime.datetime.now() - datetime.timedelta(days=30),
        amount=100,
    )
    AttendeeSubFactory(event=test_order.event, order=test_order)
    db.session.commit()

    send_monthly_event_invoice()
    event_invoice = test_order.event.invoices[0]
    assert event_invoice.amount == 10.23


def test_expire_initializing_tickets(db):
    order_expiry_time = get_settings()['order_expiry_time']
    order_old = OrderSubFactory(
        created_at=datetime.datetime.now(timezone.utc)
        - timedelta(minutes=order_expiry_time)
    )
    AttendeeSubFactory.create_batch(3, order=order_old)
    order_new = OrderSubFactory()
    AttendeeSubFactory.create_batch(2, order=order_new)
    db.session.commit()

    expire_initializing_tickets()

    assert order_old.status == 'expired'
    assert len(order_old.ticket_holders) == 0
    assert order_new.status == 'initializing'
    assert len(order_new.ticket_holders) == 2


def test_expire_pending_tickets(db):
    order_old = OrderSubFactory(
        status='pending',
        created_at=datetime.datetime.now(timezone.utc) - timedelta(minutes=45),
    )
    AttendeeSubFactory.create_batch(3, order=order_old)
    order_new = OrderSubFactory(
        status='pending',
        created_at=datetime.datetime.now(timezone.utc) - timedelta(minutes=15),
    )
    AttendeeSubFactory.create_batch(2, order=order_new)
    db.session.commit()

    expire_pending_tickets()

    assert order_old.status == 'expired'
    assert len(order_old.ticket_holders) == 3
    assert order_new.status == 'pending'
    assert len(order_new.ticket_holders) == 2

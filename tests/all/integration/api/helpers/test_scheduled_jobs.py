import datetime

from app import current_app as app, db
from app.factories.event_invoice import EventInvoiceFactory
from app.factories.attendee import AttendeeFactory
from app.models.event_invoice import EventInvoice
from app.models.ticket_holder import TicketHolder
from app.api.helpers.scheduled_jobs import event_invoices_mark_due, delete_ticket_holders_no_order_id

from tests.all.integration.utils import OpenEventTestCase


class TestScheduledJobs(OpenEventTestCase):

    def test_event_invoices_mark_due(self):
        """Method to test marking of event invoices as due"""

        with app.test_request_context():
            event_invoice_new = EventInvoiceFactory(event__ends_at=datetime.datetime(2019, 7, 20))
            event_invoice_paid = EventInvoiceFactory(status="paid")

            db.session.commit()

            event_invoice_new_id = event_invoice_new.id
            event_invoice_paid_id = event_invoice_paid.id

            event_invoices_mark_due()

            status_new = EventInvoice.query.get(event_invoice_new_id).status
            status_paid = EventInvoice.query.get(event_invoice_paid_id).status

            self.assertEqual(status_new, "due")
            self.assertNotEqual(status_paid, "due")

    def test_delete_ticket_holders_with_no_order_id(self):
        """Method to test deleting ticket holders with no order id after expiry time"""
        with app.test_request_context():
            attendee_new = AttendeeFactory()
            db.session.commit()

            attendee_new_id = attendee_new.id
            delete_ticket_holders_no_order_id()

            ticket_holder_deleted = TicketHolder.query.get(attendee_new_id)

            self.assertIsNot(ticket_holder_deleted, None)

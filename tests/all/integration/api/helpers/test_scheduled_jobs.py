import datetime

from app.api.helpers.scheduled_jobs import (
    delete_ticket_holders_no_order_id,
    event_invoices_mark_due,
)
import app.factories.common as common
from app.factories.attendee import AttendeeFactory
from app.factories.event_invoice import EventInvoiceFactory
from app.models import db
from app.models.event_invoice import EventInvoice
from app.models.ticket_holder import TicketHolder
from tests.all.integration.utils import OpenEventTestCase


class TestScheduledJobs(OpenEventTestCase):
    def test_event_invoices_mark_due(self):
        """Method to test marking of event invoices as due"""

        with self.app.test_request_context():
            event_invoice_new = EventInvoiceFactory(
                event__ends_at=datetime.datetime(2019, 7, 20)
            )
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

        with self.app.test_request_context():
            attendee = AttendeeFactory(created_at=common.date_)
            db.session.commit()
            attendee_id = attendee.id
            delete_ticket_holders_no_order_id()
            ticket_holder = TicketHolder.query.get(attendee_id)
            self.assertIs(ticket_holder, None)

    def test_delete_ticket_holder_created_currently(self):
        """Method to test not deleting ticket holders with no order id but created within expiry time"""

        with self.app.test_request_context():
            attendee = AttendeeFactory(
                created_at=datetime.datetime.utcnow(),
                modified_at=datetime.datetime.utcnow(),
            )

            db.session.commit()
            attendee_id = attendee.id
            delete_ticket_holders_no_order_id()
            ticket_holder = TicketHolder.query.get(attendee_id)
            self.assertIsNot(ticket_holder, None)

    def test_delete_ticket_holder_with_valid_order_id(self):
        """Method to test not deleting ticket holders with order id after expiry time"""

        with self.app.test_request_context():
            attendee = AttendeeFactory(
                order_id=1,
                ticket_id=1,
                created_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
                modified_at=datetime.datetime.utcnow() - datetime.timedelta(minutes=15),
            )

            db.session.commit()
            attendee_id = attendee.id
            delete_ticket_holders_no_order_id()
            ticket_holder = TicketHolder.query.get(attendee_id)
            self.assertIsNot(ticket_holder, None)

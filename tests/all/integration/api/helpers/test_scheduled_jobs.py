import datetime

from app.api.helpers.scheduled_jobs import (
    delete_ticket_holders_no_order_id,
    event_invoices_mark_due,
    send_monthly_event_invoice,
)
from app.factories.attendee import AttendeeFactory
from app.factories.ticket_fee import TicketFeesFactory
from app.factories.event_invoice import EventInvoiceFactory
from app.factories.user import UserFactory
from app.factories.event import EventFactoryBasic
from app.factories.order import OrderFactory
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
            attendee = AttendeeFactory()
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

    def test_send_monthly_invoice(self):
        """Method to test monthly invoices"""

        with self.app.test_request_context():
            # ticket fee factory
            ticket_fee_test = TicketFeesFactory()
            ticket_fee_test.service_fee = 10.23
            # event factory
            test_event = EventFactoryBasic(state='published')
            # user factory
            test_user = UserFactory()
            # order factory
            test_order = OrderFactory(status='completed')
            test_order.completed_at = datetime.datetime.now() - datetime.timedelta(
                days=30
            )
            test_order.amount = 100
            test_order.event = test_event
            # ticket holder factory
            test_ticket_holder = AttendeeFactory()
            test_event.owner = test_user
            db.session.commit()

            send_monthly_event_invoice()
            event_invoice = EventInvoice.query.get(1)
            self.assertEqual(event_invoice.amount, 100.1)

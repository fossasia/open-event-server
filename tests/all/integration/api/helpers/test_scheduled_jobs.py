import datetime

from app import current_app as app, db
from app.factories.event_invoice import EventInvoiceFactory
from app.models.event_invoice import EventInvoice
from app.api.helpers.scheduled_jobs import event_invoices_mark_due

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

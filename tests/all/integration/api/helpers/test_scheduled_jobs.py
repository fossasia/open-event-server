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
            event_invoice = EventInvoiceFactory(event__ends_at=datetime.datetime(2019, 7, 20))
            db.session.commit()
            event_invoice_id = event_invoice.id
            status_1 = EventInvoice.query.get(event_invoice_id).status

            event_invoice = EventInvoiceFactory(status="paid")
            db.session.commit()
            event_invoice_id = event_invoice.id
            status_2 = EventInvoice.query.get(event_invoice_id).status

            event_invoice = EventInvoiceFactory()
            event_invoice.created_at = datetime.datetime(2099, 12, 14)
            db.session.commit()
            event_invoice_id = event_invoice.id
            status_3 = EventInvoice.query.get(event_invoice_id).status

            event_invoices_mark_due()
            self.assertEqual(status_1, "due")
            self.assertNotEqual(status_2, "due")
            self.assertNotEqual(status_3, "due")

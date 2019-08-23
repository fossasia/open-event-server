import unittest
import datetime

from app import current_app as app
from app.api.helpers.db import save_to_db
from app.factories.event_invoice import EventInvoiceFactory
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.event_invoices import fetch_event_invoices


class TestEventInvoices(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_event_invoices_status(self):
        """Method to test function which fetches event invoices based on status."""

        with app.test_request_context():

            event_invoice1 = EventInvoiceFactory()
            event_invoice1.status = "due"
            save_to_db(event_invoice1)

            event_invoice2 = EventInvoiceFactory()
            event_invoice2.status = "paid"
            save_to_db(event_invoice2)

            event_invoice3 = EventInvoiceFactory()
            event_invoice3.status = "upcoming"
            save_to_db(event_invoice3)

            self.assertEqual(event_invoice1, fetch_event_invoices('due')[0])
            self.assertEqual(event_invoice2, fetch_event_invoices('upcoming')[0])
            self.assertEqual(event_invoice3, fetch_event_invoices('paid')[0])


if __name__ == '__main__':
    unittest.main()

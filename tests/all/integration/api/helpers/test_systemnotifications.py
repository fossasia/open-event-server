import unittest

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.system_notifications import (
    get_event_exported_actions,
    get_event_imported_actions,
    get_monthly_payment_notification_actions,
    get_monthly_payment_follow_up_notification_actions,
    get_ticket_purchased_notification_actions,
    get_ticket_purchased_attendee_notification_actions,
    get_ticket_purchased_organizer_notification_actions,
    get_event_published_notification_actions
    )
from tests.all.integration.setup_database import Setup


class TestSystemNotificationHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_get_event_exported_actions(self):
        """Method to test the actions associated with a notification about an event being successfully exported."""

        with app.test_request_context():
            request_url = 'https://localhost/some/path/image.png'
            response = get_event_exported_actions(request_url)
            self.assertIsInstance(response, list)

    def test_get_event_imported_actions(self):
        """Method to test the actions associated with a notification about an event being successfully exported."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525'
            request_event_id = 1
            response = get_event_imported_actions(request_event_id, request_url)
            self.assertIsInstance(response, list)

    def test_get_monthly_payment_notification_actions(self):
        """Method to test the actions associated with a notification of monthly payments"""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/payment'
            request_event_id = 1
            response = get_monthly_payment_notification_actions(request_event_id, request_url)
            self.assertIsInstance(response, list)

    def test_get_monthly_payment_follow_up_notification_actions(self):
        """Method to test the actions associated with a follow up notification of monthly payments."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/payment'
            request_event_id = 1
            response = get_monthly_payment_follow_up_notification_actions(request_event_id, request_url)
            self.assertIsInstance(response, list)

    def test_get_ticket_purchased_notification_actions(self):
        """Method to test the actions associated with a notification of tickets purchased."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/order'
            request_order_id = 1
            response = get_ticket_purchased_notification_actions(request_order_id, request_url)
            self.assertIsInstance(response, list)

    def test_get_ticket_purchased_attendee_notification_actions(self):
        """Method to test the actions associated with a notification of tickets purchased for an attendee that is
           not the buyer."""

        with app.test_request_context():
            request_pdfurl = 'https://localhost/pdf/e/24324/'
            response = get_ticket_purchased_attendee_notification_actions(request_pdfurl)
            self.assertIsInstance(response, list)

    def test_get_ticket_purchased_organizer_notification_actions(self):
        """Method to test the actions associated with a notification of tickets purchased for the event organizer."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/order'
            request_order_id = 1
            response = get_ticket_purchased_organizer_notification_actions(request_order_id, request_url)
            self.assertIsInstance(response, list)

    def test_get_event_published_notification_actions(self):
        """Method to test the actions associated with a notification of an event getting published."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525'
            request_event_id = 1
            response = get_event_published_notification_actions(request_event_id, request_url)
            self.assertIsInstance(response, list)


if __name__ == '__main__':
    unittest.main()

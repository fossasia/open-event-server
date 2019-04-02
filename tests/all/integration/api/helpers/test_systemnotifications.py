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
    get_event_published_notification_actions,
    get_event_role_notification_actions,
    get_new_session_notification_actions,
    get_session_schedule_notification_actions,
    get_next_event_notification_actions,
    get_session_accept_reject_notification_actions,
    get_invite_papers_notification_actions
)
from tests.all.integration.setup_database import Setup
from app.models.notification import NotificationAction


class TestSystemNotificationHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_event_exported(self):
        """Method to test the actions associated with a notification about an event being successfully exported."""

        with app.test_request_context():
            request_url = 'https://localhost/some/path/image.png'
            response = get_event_exported_actions(request_url)
            expected_action = NotificationAction(
                subject='event-export',
                link=request_url,
                action_type='download'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_event_imported(self):
        """Method to test the actions associated with a notification about an event being successfully exported."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525'
            request_event_id = 1
            response = get_event_imported_actions(request_event_id, request_url)
            expected_action = NotificationAction(
                # subject is still 'event' since the action will be to view the imported event.
                subject='event',
                link=request_url,
                subject_id=request_event_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_monthly_payment_notification(self):
        """Method to test the actions associated with a notification of monthly payments"""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/payment'
            request_event_id = 1
            response = get_monthly_payment_notification_actions(request_event_id, request_url)
            expected_action = NotificationAction(
                subject='event',
                link=request_url,
                subject_id=request_event_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_monthly_pay_followup_notification(self):
        """Method to test the actions associated with a follow up notification of monthly payments."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/payment'
            request_event_id = 1
            response = get_monthly_payment_follow_up_notification_actions(request_event_id, request_url)
            expected_action = NotificationAction(
                subject='invoice',
                link=request_url,
                subject_id=request_event_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_ticket_purchased_notification(self):
        """Method to test the actions associated with a notification of tickets purchased."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/order'
            request_order_id = 1
            response = get_ticket_purchased_notification_actions(request_order_id, request_url)
            expected_action = NotificationAction(
                subject='order',
                link=request_url,
                subject_id=request_order_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_ticket_purchased_attendee(self):
        """Method to test the actions associated with a notification of tickets purchased for an attendee that is
           not the buyer."""

        with app.test_request_context():
            request_pdfurl = 'https://localhost/pdf/e/24324/'
            response = get_ticket_purchased_attendee_notification_actions(request_pdfurl)
            expected_action = NotificationAction(
                subject='tickets-pdf',
                link=request_pdfurl,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_ticket_purchase_organizer(self):
        """Method to test the actions associated with a notification of tickets purchased for the event organizer."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/order'
            request_order_id = 1
            response = get_ticket_purchased_organizer_notification_actions(request_order_id, request_url)
            expected_action = NotificationAction(
                subject='order',
                subject_id=request_order_id,
                link=request_url,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_event_published_notification(self):
        """Method to test the actions associated with a notification of an event getting published."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525'
            request_event_id = 1
            response = get_event_published_notification_actions(request_event_id, request_url)
            expected_action = NotificationAction(
                subject='event',
                subject_id=request_event_id,
                link=request_url,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_event_role_notification(self):
        """Method to test the actions associated with a notification of an event role."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525/invitation'
            request_event_id = 1
            response = get_event_role_notification_actions(request_event_id, request_url)
            expected_action = NotificationAction(
                subject='event-role',
                subject_id=request_event_id,
                link=request_url,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_new_session_notification(self):
        """Method to test the actions associated with a notification of an event getting a new session proposal."""

        with app.test_request_context():
            request_url = 'https://localhost/e/session/345525'
            request_session_id = 1
            response = get_new_session_notification_actions(request_session_id, request_url)
            expected_action = NotificationAction(
                subject='session',
                link=request_url,
                subject_id=request_session_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_session_schedule_notification(self):
        """Method to test the actions associated with a notification of change in schedule of a session."""

        with app.test_request_context():
            request_url = 'https://localhost/e/session/345525'
            request_session_id = 1
            response = get_session_schedule_notification_actions(request_session_id, request_url)
            expected_action = NotificationAction(
                subject='session',
                link=request_url,
                subject_id=request_session_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_next_event_notification(self):
        """Method to test the actions associated with a notification of next event."""

        with app.test_request_context():
            request_url = 'https://localhost/e/345525'
            request_session_id = 1
            response = get_next_event_notification_actions(request_session_id, request_url)
            expected_action = NotificationAction(
                subject='event',
                link=request_url,
                subject_id=request_session_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_session_accept_reject_notif(self):
        """Method to test the actions associated with a notification of a session getting accepted/rejected."""

        with app.test_request_context():
            request_url = 'https://localhost/e/session/345525'
            request_session_id = 1
            response = get_session_accept_reject_notification_actions(request_session_id, request_url)
            expected_action = NotificationAction(
                subject='session',
                link=request_url,
                subject_id=request_session_id,
                action_type='view'
            )
            expected_action = [expected_action]
            expected_length = len(expected_action)
            response_length = len(response)
            self.assertIsInstance(response, list)
            self.assertEqual(expected_action[0].subject, response[0].subject)
            self.assertEqual(expected_length, response_length)

    def test_invite_papers_notification(self):
        """Method to test the actions associated with an invite to submit papers."""

        with app.test_request_context():
            request_cfs_url = 'https://localhost/e/cfs/345525'
            request_submit_url = 'https://localhost/e/cfs/345525/submit'
            response = get_invite_papers_notification_actions(request_cfs_url, request_submit_url)
            expected_cfs_action = NotificationAction(
                subject='call-for-speakers',
                link=request_cfs_url,
                action_type='view'
            )
            expected_submit_action = NotificationAction(
                subject='call-for-speakers',
                link=request_submit_url,
                action_type='submit'
            )
            expected_response = [expected_cfs_action, expected_submit_action]
            expected_response_length = len(expected_response)
            response_length = len(response)

            self.assertIsInstance(response, list)
            self.assertEqual(expected_cfs_action.subject, response[0].subject)
            self.assertEqual(expected_submit_action.subject, response[1].subject)
            self.assertEqual(expected_response_length, response_length)


if __name__ == '__main__':
    unittest.main()

import unittest
from app.api.helpers.notification import (
    send_notif_new_session_organizer,
    send_followup_notif_monthly_fee_payment,
    send_notif_after_event,
    send_notif_after_export,
    send_notif_after_import,
    send_notif_event_role,
    send_notif_monthly_fee_payment,
    send_notif_session_accept_reject,
    send_notif_ticket_purchase_organizer,
)
from app.factories.session import SessionFactory
from app.factories.user import UserFactory
from app.models.notification import Notification
from tests.all.integration.utils import OpenEventTestCase


class TestNotificationHelper(OpenEventTestCase):
    link = 'https://test.link'

    def test_send_notif_new_session_organizer(self):
        """Method to test new session notification"""
        with self.app.test_request_context():
            send_notif_new_session_organizer(
                UserFactory(), 'Hobo Meet', self.link, SessionFactory().id
            )
            notification = Notification.query.first()
            self.assertEqual(notification.title, 'New session proposal for Hobo Meet')
            self.assertEqual(
                notification.message,
                'The event <strong>Hobo Meet</strong> has received a new session '
                'proposal.',
            )

    def test_send_notif_session_accept_reject(self):
        """Method to test session accept reject notification"""
        with self.app.test_request_context():
            send_notif_session_accept_reject(
                UserFactory(),
                'Homeless Therapy',
                'accepted',
                self.link,
                SessionFactory().id,
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title, 'Session Homeless Therapy has been accepted'
            )
            self.assertEqual(
                notification.message,
                'The session <strong>Homeless Therapy</strong> has been '
                '<strong>accepted</strong> by the Organizer.',
            )

    def test_send_notif_after_import(self):
        """Method to test notification after import"""
        with self.app.test_request_context():
            send_notif_after_import(
                UserFactory(),
                event_name='Tooth Fairy Convention',
                error_text='TOOTH_NOT_FOUND',
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title, 'Import of event Tooth Fairy Convention failed'
            )
            self.assertEqual(
                notification.message,
                'The following error occurred:<br><pre>TOOTH_NOT_FOUND</pre>',
            )

    def test_send_notif_after_export(self):
        """Method to test notification after export"""
        with self.app.test_request_context():
            send_notif_after_export(
                UserFactory(), 'Elf Gather', self.link, 'SLEIGH_BROKEN'
            )
            notification = Notification.query.first()
            self.assertEqual(notification.title, 'Export of event Elf Gather failed')
            self.assertEqual(
                notification.message,
                'The following error occurred:<br><pre>SLEIGH_BROKEN</pre>',
            )

    def test_send_notif_monthly_fee_payment(self):
        """Method to test monthly fee payment notification"""
        with self.app.test_request_context():
            send_notif_monthly_fee_payment(
                UserFactory(), 'Pizza Party', 'October', 563.65, 'Kite', self.link, 1
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title,
                'October - Monthly service fee invoice for Pizza Party',
            )
            self.assertEqual(
                notification.message,
                'The total service fee for the ticket sales of Pizza Party in the '
                'month of October is 563.65.<br/> That payment for the same has to '
                'be made in two weeks.<br><br><em>Thank you for using Kite.</em>',
            )

    def test_send_followup_notif_monthly_fee_payment(self):
        """Method to test follow up monthly fee payment notification"""
        with self.app.test_request_context():
            send_followup_notif_monthly_fee_payment(
                UserFactory(),
                'Champagne Showers',
                'November',
                4532.99,
                'RedFoo',
                self.link,
                1,
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title,
                'Past Due: November - Monthly service fee invoice for Champagne Showers',
            )
            self.assertEqual(
                notification.message,
                'The total service fee for the ticket sales of Champagne Showers '
                'in the month of November is 4532.99.<br/> That payment for the '
                'same is past the due date.<br><br><em>Thank you for using '
                'RedFoo.</em>',
            )

    def test_send_notif_event_role(self):
        """Method to test event role invite notification"""
        with self.app.test_request_context():
            send_notif_event_role(
                UserFactory(), 'Dinosaur', 'Mass Extinction', self.link, 1
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title, 'Invitation to be Dinosaur at Mass Extinction',
            )
            self.assertEqual(
                notification.message,
                "You've been invited to be one of the <strong>Dinosaurs</strong> at <strong>Mass Extinction</strong>.",
            )

    def test_send_notif_after_event(self):
        """Method to test notification after conclusion"""
        with self.app.test_request_context():
            send_notif_after_event(UserFactory(), 'Apocalypse')
            notification = Notification.query.first()
            self.assertEqual(notification.title, 'Event Apocalypse completed')
            self.assertEqual(
                notification.message,
                'The event <strong>Apocalypse</strong> has been completed.<br><br>',
            )

    def test_send_notif_ticket_purchase_organizer(self):
        """Method to test order invoice notification after purchase"""
        with self.app.test_request_context():
            send_notif_ticket_purchase_organizer(
                UserFactory(), 's53js79zgd', self.link, 'Poodle', 1
            )
            notification = Notification.query.first()
            self.assertEqual(
                notification.title, 'New ticket purchase for Poodle : (s53js79zgd)'
            )
            self.assertEqual(
                notification.message, 'The order has been processed successfully.'
            )


if __name__ == '__main__':
    unittest.main()

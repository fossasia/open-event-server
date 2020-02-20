import unittest
from app.models import db
from flask import current_app
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
from app.api.helpers.db import save_to_db
import app.factories.common as common
from app.factories.session import SessionFactory
from app.factories.user import UserFactory
from app.models.notification import Notification
from tests.all.integration.utils import OpenEventTestCase


class TestNotificationHelper(OpenEventTestCase):
    def test_send_notif_new_session_organizer(self):
        """Method to test new session notification"""
        with self.app.test_request_context():
            user = UserFactory()
            test_session = SessionFactory()
            link = common.url_
            event_name = common.string_
            current_app.config['TESTING'] = False
            send_notif_new_session_organizer(user, event_name, link, test_session.id)
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_session_accept_reject(self):
        """Method to test session accept reject notification"""
        with self.app.test_request_context():
            user = UserFactory()
            test_session = SessionFactory()
            link = common.url_
            session_name = common.string_
            acceptance = common.string_
            current_app.config['TESTING'] = False
            send_notif_session_accept_reject(
                user, session_name, acceptance, link, test_session.id
            )
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_after_import(self):
        """Method to test notification after import"""
        with self.app.test_request_context():
            user = UserFactory()
            event_name = common.string_
            error_text = common.string_
            current_app.config['TESTING'] = False
            send_notif_after_import(user, event_name=event_name, error_text=error_text)
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_after_export(self):
        """Method to test notification after export"""
        with self.app.test_request_context():
            user = UserFactory()
            event_name = common.string_
            download_url = common.url_
            error_text = common.string_
            current_app.config['TESTING'] = False
            send_notif_after_export(user, event_name, download_url, error_text)
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_monthly_fee_payment(self):
        """Method to test monthly fee payment notification"""
        with self.app.test_request_context():
            user = UserFactory()
            link = common.url_
            previous_month = common.string_
            amount = 1
            app_name = common.string_
            event_name = common.string_
            event_id = 1
            current_app.config['TESTING'] = False
            send_notif_monthly_fee_payment(
                user, event_name, previous_month, amount, app_name, link, event_id
            )
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_followup_notif_monthly_fee_payment(self):
        """Method to test follow up monthly fee payment notification"""
        with self.app.test_request_context():
            user = UserFactory()
            link = common.url_
            previous_month = "January"
            amount = 1
            app_name = common.string_
            event_name = common.string_
            event_id = 1
            current_app.config['TESTING'] = False
            send_followup_notif_monthly_fee_payment(
                user, event_name, previous_month, amount, app_name, link, event_id
            )
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_event_role(self):
        """Method to test event role invite notification"""
        with self.app.test_request_context():
            user = UserFactory()
            role_name = common.string_
            link = common.url_
            event_name = common.string_
            event_id = 1
            current_app.config['TESTING'] = False
            send_notif_event_role(user, role_name, event_name, link, event_id)
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_after_event(self):
        """Method to test notification after conclusion"""
        with self.app.test_request_context():
            user = UserFactory()
            event_name = common.string_
            current_app.config['TESTING'] = False
            send_notif_after_event(user, event_name)
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])

    def test_send_notif_ticket_purchase_organizer(self):
        """Method to test order invoice notification after purchase"""
        with self.app.test_request_context():
            user = UserFactory()
            invoice_id = 1
            order_url = common.url_
            event_name = common.string_
            subject_id = 1
            current_app.config['TESTING'] = False
            send_notif_ticket_purchase_organizer(
                user, invoice_id, order_url, event_name, subject_id
            )
            notif_ = Notification.query.all()
            self.assertIsNotNone(notif_[0])


if __name__ == '__main__':
    unittest.main()

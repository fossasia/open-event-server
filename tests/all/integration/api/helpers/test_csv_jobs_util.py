from app import current_app as app
from tests.all.integration.auth_helper import create_user
from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup
from app.api.helpers.csv_jobs_util import *
from app.factories.attendee import AttendeeFactory
from app.factories.order import OrderFactory
from app.factories.session import SessionFactory
from app.factories.speaker import SpeakerFactory
from app.models import db
import app.factories.common as common

import unittest


class TestExportCSV(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def test_export_orders_csv(self):
        """Method to check the orders data export"""

        with app.test_request_context():
            test_order = OrderFactory()
            test_order.amount = 2
            field_data = export_orders_csv([test_order])
            self.assertEqual(field_data[1][2], 'pending')
            self.assertEqual(field_data[1][4], '2')

    def test_export_attendees_csv(self):
        """Method to check the attendees data export"""

        with app.test_request_context():
            test_attendee = AttendeeFactory()
            field_data = export_attendees_csv([test_attendee])
            self.assertEqual(field_data[1][3], common.string_)
            self.assertEqual(field_data[1][5], 'user0@example.com')

    def test_export_sessions_csv(self):
        """Method to check sessions data export"""

        with app.test_request_context():
            test_session = SessionFactory()
            field_data = export_sessions_csv([test_session])
            self.assertEqual(field_data[1][6], common.int_)
            self.assertEqual(field_data[1][7], 'accepted')

    def test_export_speakers_csv(self):
        """Method to check speakers data export"""

        with app.test_request_context():
            test_speaker = SpeakerFactory()
            user = create_user(email='export@example.com', password='password')
            user.id = 2
            field_data = export_speakers_csv([test_speaker])
            self.assertEqual(field_data[1][0], common.string_)
            self.assertEqual(field_data[1][1], 'user0@example.com')


if __name__ == '__main__':
    unittest.main()
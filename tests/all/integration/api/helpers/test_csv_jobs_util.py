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


    def test_export_orders_csv(self):
        """Method to check the orders data export"""

        with app.test_request_context():
            test_order = OrderFactory()
            test_order.amount = 2
            field_data = export_orders_csv([test_order])
            self.assertEqual(field_data[1][2], 'initializing')
            self.assertEqual(field_data[1][4], '2')

    def test_export_attendees_csv(self):
        """Method to check the attendees data export"""

        with app.test_request_context():
            test_attendee = AttendeeFactory()
            field_data = export_attendees_csv([test_attendee])
            self.assertEqual(field_data[1][3], common.string_)
            self.assertEqual(field_data[1][5], 'user0@example.com')

    def _test_export_session_csv(self, test_session=None):
        with app.test_request_context():
            if not test_session:
                test_session = SessionFactory()
            field_data = export_sessions_csv([test_session])
            session_row = field_data[1]

            self.assertEqual(session_row[0], 'example (accepted)')
            self.assertEqual(session_row[7], 'accepted')

    def test_export_sessions_csv(self):
        """Method to check sessions data export"""

        with app.test_request_context():
            self._test_export_session_csv()
    
    def test_export_sessions_none_csv(self):
        """Method to check sessions data export with no abstract"""

        with app.test_request_context():
            test_session = SessionFactory()
            test_session.long_abstract = None
            test_session.level = None
            self._test_export_session_csv(test_session)

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
from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup
from app.api.helpers.csv_jobs_util import *
from app.models.order import Order
from app.models.ticket_holder import TicketHolder
from app.models.session import Session
from app.models.speaker import Speaker
from app.factories.attendee import AttendeeFactory
from app.factories.order import OrderFactory
from app.factories.session import SessionFactory
from app.factories.speaker import SpeakerFactory
from app.models import db


import unittest


class TestExportCSV(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def test_export_orders_csv(self):
        """Method to check the orders data export"""

        with app.test_request_context():
            test_order = OrderFactory()
            check_order = db.session.query(Order).filter_by(id=test_order.id).first()
            self.assertEqual(export_orders_csv([check_order]), export_orders_csv([test_order]))

    def test_export_attendees_csv(self):
        """Method to check the attendees data export"""

        with app.test_request_context():
            test_attendee = AttendeeFactory()
            check_attendee = db.session.query(TicketHolder).filter_by(id=test_attendee.id)
            self.assertEqual(export_attendees_csv([check_attendee]), export_attendees_csv([test_attendee]))


    def test_export_sessions_csv(self):
        """Method to check sessions data export"""

        with app.test_request_context():
            test_session = SessionFactory()
            check_session = db.session.query(Session).filter_by(id=test_session.id)
            self.assertEqual(export_sessions_csv([check_session]), export_sessions_csv([test_session]))


    def test_export_speakers_csv(self):
        """Method to check speakers data export"""

        with app.test_request_context():
            test_speaker = SpeakerFactory()
            check_speaker = db.session.query(Speaker).filter_by(id=test_speaker.id)
            self.assertEqual(export_speakers_csv([check_speaker]), export_speakers_csv([test_speaker]))


if __name__ == '__main__':
    unittest.main()

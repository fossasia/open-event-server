from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup
from app.models.user import User
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from tests.all.integration.auth_helper import create_user
from app.models import db

import unittest

class TestExportCSV(OpenEventTestCase):

    def setUp(self):
        self.app = Setup.create_app()

    def test_export_orders_csv(self):
        """Method to check the orders data export"""

        with app.test_request_context():
            test_user = create_user(email='authtest@gmail.com', password='password')
            test_order = Order(quantity=2, amount=200, address="Test Address", city="Brooklyn",
                               state="New York", country="USA", zipcode=10234, transaction_id="TEST123", paid_via="VISA",
                               user_id=db.session.query(User).get(test_user.id), discount_code_id="TESTDISC",
                               event_id="919191", payment_mode="online", order_notes="This is a test order")
            data = export_orders_csv(test_order)
            self.assertEqual(len(data[1]), 10)

    def test_export_attendees_csv(self):
        """Method to check the attendees data export"""

        with app.test_request_context():
            test_user = create_user(email='authtest@gmail.com', password='password')
            test_order = Order(quantity=2, amount=200, address="Test Address", city="Brooklyn",
                               state="New York", country="USA", zipcode=10234, transaction_id="TEST123", paid_via="VISA",
                               user_id=db.session.query(User).get(test_user.id), discount_code_id="TESTDISC",
                               event_id="919191", payment_mode="online", order_notes="This is a test order")
            data = export_attendees_csv(test_user)
            self.assertEqual(len(data[1]), 11)

    def test_export_sessions_csv(self):
        """Method to check sessions data export"""

        with app.test_request_context():
            session = Session(title="Test Session", subtitle="Test Subtitle",
                    short_abstract="test short_abstract", long_abstract="test long_abstract",
                    level="Advanced", type="AI")
            data = export_sessions_csv(session)
            self.assertEqual(len(data[1]), 10)

    def test_export_speakers_csv(self):
        """Method to check speakers data export"""

        with app.test_request_context():
            speaker = Speaker(name="test", email="test@gmail.com", mobile="0000000000", organisation="testorg",
                              short_biography="This is a test speaker", position="test-position")
            session = Session(title="Test Session", subtitle="Test Subtitle",short_abstract="test short_abstract",
                              long_abstract="test long_abstract", level="Advanced", type="AI")
            data = export_speakers_csv(speaker)
            self.assertEqual(len(data[1]), 7)


if __name__ == '__main__':
    unittest.main()

import unittest
from datetime import timedelta, datetime, timezone

from app import current_app as app, db
from app.api.helpers.db import save_to_db
from app.api.helpers.order import set_expiry_for_order, delete_related_attendees_for_order
from app.factories.attendee import AttendeeFactory
from app.factories.event import EventFactoryBasic
from app.factories.order import OrderFactory
from app.models.order import Order
from app.api.helpers.db import save_to_db
from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase


class TestOrderUtilities(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_should_expire_outdated_order(self):
        """Method to test expiration of outdated orders"""

        with app.test_request_context():
            obj = OrderFactory()
            event = EventFactoryBasic()
            obj.event = event
            obj.created_at = datetime.now(timezone.utc) - timedelta(
                minutes=obj.event.order_expiry_time)
            set_expiry_for_order(obj)
            self.assertEqual(obj.status, 'expired')

    def test_should_not_expire_valid_orders(self):
        """Method to test to not mark valid orders as expired"""

        with app.test_request_context():
            obj = OrderFactory()
            event = EventFactoryBasic()
            obj.event = event
            set_expiry_for_order(obj)
            self.assertEqual(obj.status, 'pending')

    def test_should_delete_related_attendees(self):
        """Method to test to delete related attendees of an event"""

        with app.test_request_context():
            attendee = AttendeeFactory()
            save_to_db(attendee)

            obj = OrderFactory()
            obj.ticket_holders = [attendee, ]
            save_to_db(obj)

            delete_related_attendees_for_order(obj)
            order = db.session.query(Order).filter(Order.id == obj.id).first()
            self.assertEqual(len(order.ticket_holders), 0)


if __name__ == '__main__':
    unittest.main()

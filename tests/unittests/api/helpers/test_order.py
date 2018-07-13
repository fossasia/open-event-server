import unittest
from datetime import timedelta, datetime, timezone

from app import current_app as app
from app.api.helpers import ticketing
from app.api.helpers.order import set_expiry_for_order
from app.factories.order import OrderFactory
from tests.unittests.setup_database import Setup
from tests.unittests.utils import OpenEventTestCase


class TestOrderUtilities(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_should_expire_outdated_order(self):
        with app.test_request_context():
            obj = OrderFactory()
            obj.created_at = datetime.now(timezone.utc) - timedelta(
                minutes=ticketing.TicketingManager.get_order_expiry() + 10)
            set_expiry_for_order(obj)
            self.assertEqual(obj.status, 'expired')

    def test_should_not_expire_valid_orders(self):
        with app.test_request_context():
            obj = OrderFactory()
            set_expiry_for_order(obj)
            self.assertEqual(obj.status, 'pending')


if __name__ == '__main__':
    unittest.main()

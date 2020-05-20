import datetime

from app.api.helpers.humanize_helper import humanize_helper
from tests.factories.order import OrderFactory

class TestHumanizeHelper(OpenEventTestCase): 
    def test_humanize_helper(self):
        """Method to test humanization of order creation time"""

        with self.app.test_request_context():
            test_order = OrderFactory(created_at=datetime.datetime.now() 
                                        - datetime.timedelta(days=10))
            actual_response = humanize_helper(test_order.created_at)
            expected_response = '10 days ago'
            self.assertEqual(actual_response, expected_response)
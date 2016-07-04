import unittest

from tests.api.utils import get_path, create_services, create_event
from test_put_api import TestPutApiBase
from open_event import current_app as app
from tests.setup_database import Setup
from test_post_api_validation import ApiValidationTestCase


class TestPutApiValidation(TestPutApiBase, ApiValidationTestCase):
    """
    Tests the input validation in PUT API
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event_id = create_event(name='TestEvent_1')
            create_services(event_id)


    def _test_model(self, name, data, fields=[]):
        """
        Sets a random value to each of the :fields in :data and makes
        sure PUT request failed.
        At last check if original value had prevailed
        """
        path = get_path(1) if name == 'event' else get_path(1, name + 's', 1)
        self._login_user()
        for field in fields:
            data_copy = data.copy()
            data_copy[field] = 'r@nd0m_g00d_for_n0thing_v@lue'
            response = self._put(path, data_copy)
            self.assertEqual(response.status_code, 400)
        # make sure field is not updated
        response = self.app.get(path)
        self.assertIn('Test%s_1' % str(name).title(), response.data)
        self.assertNotIn('"Test%s"' % str(name).title(), response.data)


if __name__ == '__main__':
    unittest.main()

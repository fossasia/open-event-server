import unittest

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.system_notifications import get_event_exported_actions, get_event_imported_actions
from tests.all.integration.setup_database import Setup


class TestSystemNotificationHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_get_event_exported_actions(self):
        """Method to test the actions associated with a notification about an event being successfully exported."""

        with app.test_request_context():
            request_url = 'https://localhost/some/path/image.png'
            response = get_event_exported_actions(request_url)
            self.assertIsInstance(response, list)


if __name__ == '__main__':
    unittest.main()

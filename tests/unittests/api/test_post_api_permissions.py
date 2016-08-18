import unittest
import json

from tests.unittests.setup_database import Setup
from tests.unittests.api.utils import create_event, get_path
from tests.unittests.utils import OpenEventTestCase
from test_post_api_auth import PostApiAuthTestCase
from tests.unittests.auth_helper import register
from app import current_app as app


# Post API Permissions Success is being already sort of
# tested in test_post_api_auth


class TestPostApiPermissionDenied(PostApiAuthTestCase, OpenEventTestCase):
    """
    Test 403 permission denied in Post API
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'myemail@gmail.com', u'test')
            create_event()  # no creator_email, no organizer is set
            # logout(self.app)  # no need for this test

    def _test_model(self, name, data):
        if name == 'event':
            return
        with app.test_request_context():
            path = get_path() if name == 'event' else get_path(1, name + 's')
            response = self.app.post(
                path,
                data=json.dumps(data),
                headers={
                    'content-type': 'application/json'
                }
            )
            self.assertEqual(response.status_code, 403)  # permission denied


if __name__ == '__main__':
    unittest.main()

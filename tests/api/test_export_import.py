import unittest

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path, create_services
from tests.api.utils_post_data import *
from open_event import current_app as app


class TestEventExport(OpenEventTestCase):
    """
    Test export of event
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            create_event()
            create_services(1)

    def test_export_success(self):
        path = get_path(1, 'export', 'json')
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('event1.zip', resp.headers['Content-Disposition'])
        size = len(resp.data)
        with app.test_request_context():
            create_services(1, '2')
            create_services(1, '3')
        # check if size increased
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(len(resp.data) > size)

    def test_export_no_event(self):
        path = get_path(2, 'export', 'json')
        resp = self.app.get(path)
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()

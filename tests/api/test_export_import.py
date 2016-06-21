import unittest
import json
from StringIO import StringIO

from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from tests.api.utils import create_event, get_path, create_services,\
    create_session
from tests.auth_helper import register
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


class TestEventImport(OpenEventTestCase):
    """
    Test import of event
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(creator_email='test@example.com')
            create_services(1, '1')
            create_services(1, '2')
            create_services(1, '3')

    def _upload(self, data, url, filename='anything'):
        return self.app.post(
            url,
            data={'file': (StringIO(data), filename)}
        )

    def _test_import_success(self):
        # first export
        path = get_path(1, 'export', 'json')
        resp = self.app.get(path)
        file = resp.data
        self.assertEqual(resp.status_code, 200)
        # import
        upload_path = get_path('import', 'json')
        resp = self._upload(file, upload_path, 'event.zip')
        self.assertEqual(resp.status_code, 200)
        # check internals
        dic = json.loads(resp.data)
        self.assertEqual(dic['id'], 2)
        self.assertEqual(dic['name'], 'TestEvent')
        self.assertIn('fb.com', dic['social_links'], dic)
        # No errors generally means everything went fine
        # The method will crash and return 500 in case of any problem

    def test_import_simple(self):
        self._test_import_success()

    def test_import_extended(self):
        with app.test_request_context():
            create_session(
                1, '4', track=1, session_type=1,
                microlocation=1, speakers=[2, 3])
            create_session(
                1, '5', track=2, speakers=[1]
            )
        self._test_import_success()


if __name__ == '__main__':
    unittest.main()

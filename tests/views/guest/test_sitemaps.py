import unittest

from open_event.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from tests.auth_helper import register
from tests.setup_database import Setup
from tests.utils import OpenEventTestCase
from open_event import current_app as app


class TestSitemaps(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')

    def test_index(self):
        resp = self.app.get('/sitemap.xml')
        self.assertEqual(resp.status_code, 200)
        self.assertIn('pages.xml.gz', resp.data)
        self.assertNotIn('1.xml.gz', resp.data)
        self.assertIn('sitemap', resp.data)

    def test_index_with_event(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event)
        resp = self.app.get('/sitemap.xml')
        self.assertIn('1.xml.gz', resp.data)

    def test_event_page(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event)
        resp = self.app.get('/sitemaps/events/1.xml.gz')
        self.assertIn('/1/', resp.data)

    def test_event_page_not_exist(self):
        resp = self.app.get('/sitemaps/events/2.xml.gz')
        self.assertEqual(resp.status_code, 404)


if __name__ == '__main__':
    unittest.main()

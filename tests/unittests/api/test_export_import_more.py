"""
Import/Export to other formats tests
- pentabarf, ical, xcal
"""
import json
import unittest

from app import current_app as app
from tests.unittests.api.utils import create_event, create_services, create_session
from tests.unittests.auth_helper import register
from tests.unittests.setup_database import Setup
from test_export_import import ImportExportBase


class ImportExportOtherBase(ImportExportBase):
    """
    Base class
    """
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            register(self.app, u'test@example.com', u'test')
            create_event(
                creator_email='test@example.com', location_name='Science Centre, Singapore',
                latitude=87.5, longitude=88.5
            )
            create_services(1, '1')
            create_session(1, '2', state='accepted', track=1, microlocation=1, speakers=[1], session_type=1)

    def _publishEvent(self, event_id):
        resp = self._put(
            '/api/v1/events/%s' % event_id,
            {'state': 'Published', 'schedule_published_on': '2017-01-01 23:11:44', 'has_session_speakers': True}
        )
        self.assertEqual(resp.status_code, 200)


class TestPentabarf(ImportExportOtherBase):
    """
    Test Pentabarf import/exports
    """
    def test_export_import(self):
        """
        test export and import of pentabarf
        """
        self._publishEvent(1)
        resp = self.app.get('/api/v1/events/1')
        identifier = json.loads(resp.data).get('identifier')
        # export
        resp = self.app.get('/e/%s/schedule/pentabarf.xml' % identifier)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('conference', resp.data)
        print resp.data
        # upload back
        resp = self._upload(resp.data, '/api/v1/events/import/pentabarf', 'pb.xml')
        self.assertEqual(resp.status_code, 200)
        # this resp is celery task, sync so done already
        data = json.loads(self.app.get('/api/v1/events/2').data)
        self.assertEqual(data['id'], 2)


class TestIcal(ImportExportOtherBase):
    """
    Test ical import/exports
    """
    def test_export_import(self):
        """
        test export and import of ical
        """
        self._publishEvent(1)
        resp = self.app.get('/api/v1/events/1')
        identifier = json.loads(resp.data).get('identifier')
        # export
        resp = self.app.get('/e/%s/schedule/calendar.ics' % identifier)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('BEGIN:VEVENT', resp.data)
        self.assertIn('TestSpeaker', resp.data)
        # import back
        resp = self._upload(resp.data, '/api/v1/events/import/ical', 'cal.ics')  # celery task response
        self.assertEqual(resp.status_code, 200)
        data = self.app.get('/api/v1/events/2').data
        self.assertIn('TestEvent', data)
        data = self.app.get('/api/v1/events/2/speakers').data
        self.assertIn('TestSpeaker', data)


class TestXcal(ImportExportOtherBase):
    """
    Test xcal import/exports
    """
    def test_export_import(self):
        """
        test export and import of xcal
        """
        self._publishEvent(1)
        resp = self.app.get('/api/v1/events/1')
        identifier = json.loads(resp.data).get('identifier')
        # export
        resp = self.app.get('/e/%s/schedule/calendar.xcs' % identifier)
        self.assertEqual(resp.status_code, 200)
        self.assertIn('TestSpeaker', resp.data)
        self.assertIn('TestSession', resp.data)
        print resp.data
        # import not made yet


if __name__ == '__main__':
    unittest.main()

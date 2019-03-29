import unittest
import icalendar
from app import current_app as app

from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app.factories.session import SessionFactory
from app.api.helpers.ICalExporter import ICalExporter


class TestICalExporter(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_export(self):
        """Test to export ical format event"""
        with app.test_request_context():
            test_session = SessionFactory()
            icalexport_object = ICalExporter()
            test_cal_str = icalexport_object.export(test_session.event_id)
            test_cal = icalendar.Calendar.from_ical(test_cal_str)
            self.assertEqual(test_cal['x-wr-calname'], 'example')
            self.assertEqual(test_cal['x-wr-caldesc'],  'Schedule for sessions at example')


if __name__ == '__main__':
    unittest.main()

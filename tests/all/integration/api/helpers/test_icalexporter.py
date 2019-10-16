import unittest
import icalendar
from app import current_app as app

from tests.all.integration.setup_database import Setup
from app.api.helpers.db import save_to_db
from app.models import db
from app.models.event import Event
from app.models.speaker import Speaker
from app.models.session import Session

from tests.all.integration.utils import OpenEventTestCase
from app.factories.session import SessionFactory
from app.factories.speaker import SpeakerFactory
from app.factories.event import EventFactoryBasic
from app.api.helpers.ICalExporter import ICalExporter


class TestICalExporter(OpenEventTestCase):

    def test_export_basic(self):
        """Test to export ical format event"""
        with app.test_request_context():
            test_session = SessionFactory()
            icalexport_object = ICalExporter()
            test_cal_str = icalexport_object.export(test_session.event_id)
            test_cal = icalendar.Calendar.from_ical(test_cal_str)
            self.assertEqual(test_cal['x-wr-calname'], 'example')
            self.assertEqual(test_cal['x-wr-caldesc'],  'Schedule for sessions at example')

    def test_export_subcomponents(self):
        """Test to check presence of subcomponents"""
        with app.test_request_context():
            test_session = SessionFactory(event__identifier='abcd')

            speaker = SpeakerFactory(name="xyz", email="test@xyz.com")
            test_session.speakers = [speaker]

            test_cal = icalendar.Calendar.from_ical(ICalExporter().export(test_session.event_id))
            
            cal_content_lines = test_cal.content_lines()
            self.assertIn('URL:http://localhost/v1/events?identifier={}'.format(test_session.event.identifier),
                          cal_content_lines)
            self.assertIn('LOCATION:example', cal_content_lines)
            self.assertIn('ATTENDEE;CN=xyz:MAILTO:test@xyz.com', cal_content_lines)


if __name__ == '__main__':
    unittest.main()

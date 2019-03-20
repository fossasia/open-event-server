import unittest

from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app import current_app as app
from app.api.helpers.xcal import XCalExporter
from xml.etree.ElementTree import fromstring, tostring

from app.factories.event import EventFactoryBasic
from app.api.helpers.db import save_to_db


class TestXCalExport(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_export(self):
        """Test to check event contents in xCal format"""
        with app.test_request_context():
            test_event = EventFactoryBasic()
            save_to_db(test_event)
            xcal = XCalExporter()
            xcal_string = xcal.export(test_event.id)
            xcal_original = fromstring(xcal_string)
            self.assertEqual(fromstring(tostring(xcal_original))[0][3].text, "example")
            self.assertEqual(fromstring(tostring(xcal_original))[0][2].text, "Schedule for sessions at example")


if __name__ == '__main__':
    unittest.main()

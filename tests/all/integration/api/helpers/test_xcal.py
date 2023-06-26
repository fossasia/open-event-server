import unittest
from xml.etree.ElementTree import fromstring, tostring

from app.api.helpers.db import save_to_db
from app.api.helpers.xcal import XCalExporter
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.event import EventFactoryBasic


class TestXCalExport(OpenEventTestCase):
    def test_export(self):
        """Test to check event contents in xCal format"""
        with self.app.test_request_context():
            test_event = EventFactoryBasic()
            save_to_db(test_event)
            xcal = XCalExporter()
            xcal_string = xcal.export(test_event.id)
            xcal_original = fromstring(xcal_string)
            assert fromstring(tostring(xcal_original))[0][3].text == "example"
            assert (
                fromstring(tostring(xcal_original))[0][2].text
                == "Schedule for sessions at example"
            )


if __name__ == '__main__':
    unittest.main()

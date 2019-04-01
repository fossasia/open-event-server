import unittest

from tests.all.integration.setup_database import Setup
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.pentabarfxml import PentabarfExporter
from xml.etree.ElementTree import fromstring, tostring
from app import current_app as app
from app.api.helpers.db import save_to_db

from app.factories.event import EventFactoryBasic

class TestPentabarfXML(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_export(self):
        """Test to check event contents in pentabarfxml format"""
        with app.test_request_context():
            test_event = EventFactoryBasic()
            save_to_db(test_event)
            pentabarf_export = PentabarfExporter()
            pentabarf_string = pentabarf_export.export(test_event.id)
            pentabarf_original = fromstring(pentabarf_string)
            self.assertEqual(fromstring(tostring(pentabarf_original))[0][0].text, "example")
            self.assertEqual(fromstring(tostring(pentabarf_original))[0][1].text, "2099-12-13")


if __name__ == '__main__':
    unittest.main()

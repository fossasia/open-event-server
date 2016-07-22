import unittest

from flask import url_for

from app.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from app import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase

class TestExport(OpenEventViewTestCase):
    def test_export_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            rv = self.app.get(url_for('event_export.display_export_view', event_id=event.id), follow_redirects=True)
            self.assertTrue("Export" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

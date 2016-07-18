import unittest

from flask import url_for

from app.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from app import current_app as app
from tests.views.view_test_case import OpenEventViewTestCase
from app.helpers.data_getter import DataGetter


class TestScheduler(OpenEventViewTestCase):
    def test_scheduler_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            rv = self.app.get(url_for('event_scheduler.display_view', event_id=event.id), follow_redirects=True)
            self.assertTrue("Scheduler" in rv.data, msg=rv.data)

    def test_scheduler_publish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            rv = self.app.get(url_for('event_scheduler.publish', event_id=event.id), follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertTrue(event.schedule_published_on is not None, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

import unittest

from flask import url_for
from werkzeug.datastructures import ImmutableMultiDict

from app import current_app as app
from app.api.events import EVENT_POST
from app.api.helpers.helpers import fix_attribute_names
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.models.modules import Module
from tests.unittests.api.utils_post_data import POST_EVENT_DATA
from tests.unittests.object_mother import ObjectMother
from tests.unittests.views.view_test_case import OpenEventViewTestCase


class TestEvents(OpenEventViewTestCase):
    def test_events_list(self):
        with app.test_request_context():
            url = url_for('events.index_view')
            rv = self.app.get(url, follow_redirects=True)

            self.assertTrue("Manage Events" in rv.data, msg=rv.data)

    def test_events_create(self):
        with app.test_request_context():
            url = url_for('events.create_view')
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Create Event" in rv.data, msg=rv.data)

    def test_event_view(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.details_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("event1" in rv.data, msg=rv.data)
            microlocation = ObjectMother.get_microlocation(event_id=event.id)
            track = ObjectMother.get_track(event_id=event.id)
            cfs = ObjectMother.get_cfs(event_id=event.id)
            save_to_db(track, "Track saved")
            save_to_db(microlocation, "Microlocation saved")
            save_to_db(cfs, "Call for speakers saved")
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("event1" in rv.data, msg=rv.data)

    def test_event_publish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.publish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Published", event.state, msg=event.state)

    def test_event_unpublish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.state = "Published"
            save_to_db(event, "Event saved")
            url = url_for('events.unpublish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Draft", event.state, msg=event.state)

    def test_event_delete(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.trash_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Your event has been deleted" in rv.data, msg=rv.data)

    def test_event_copy(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            url = url_for('events.copy_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Copy of event1" in rv.data, msg=rv.data)


if __name__ == '__main__':
    unittest.main()

import unittest

from tests.api.utils_post_data import POST_EVENT_DATA
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.helpers.data_getter import DataGetter
from flask import url_for

from tests.views.view_test_case import OpenEventViewTestCase


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

    def test_events_create_post(self):
        with app.test_request_context():
            url = url_for('events.create_view')
            data = POST_EVENT_DATA
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=data)
            self.assertTrue(POST_EVENT_DATA['name'] in rv.data, msg=rv.data)

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
            url = url_for('events.delete_view', event_id=event.id)
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

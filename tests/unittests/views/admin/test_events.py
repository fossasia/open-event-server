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

    def test_events_edit(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            save_to_db(event, "Event saved")
            custom_forms = ObjectMother.get_custom_form(event.id)
            save_to_db(custom_forms, "Custom forms saved")
            url = url_for('events.edit_view', event_id=event.id)
            data = fix_attribute_names(POST_EVENT_DATA.copy(), EVENT_POST)
            del data['copyright']
            del data['call_for_papers']
            data['payment_country'] = 'United States'
            data['payment_currency'] = 'USD United States Dollars $'
            data['sponsors_state'] = 'on'
            data['sponsors[name]'] = ['Sponsor 1', 'Sponsor 2']
            data['sponsors[type]'] = ['Gold', 'Silver']
            data['sponsors[url]'] = ["", ""]
            data['sponsors[logo]'] = ["", ""]
            data['sponsors[description]'] = ["", ""]
            data['sponsors[level]'] = ["", ""]
            data['name'] = 'EditTestName'
            data['start_date'] = '07/04/2016'
            data['start_time'] = '19:00'
            data['has_session_speakers'] = 'yes'
            data['end_date'] = '07/04/2016'
            data['end_time'] = '22:00'
            data['has_session_speakers'] = 'no'
            data['custom_form[name]'] = ['session_form', 'speaker_form']
            data['custom_form[value]'] = [custom_forms.session_form, custom_forms.speaker_form]
            data = ImmutableMultiDict(data)
            rv = self.app.post(url, follow_redirects=True, buffered=True, content_type='multipart/form-data',
                               data=data)
            self.assertTrue('EditTestName' in rv.data, msg=rv.data)
            self.assertTrue(data['sponsors[name]'] in rv.data, msg=rv.data)

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

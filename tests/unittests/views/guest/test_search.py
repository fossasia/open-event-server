import unittest
import urllib
from datetime import datetime,timedelta

from flask import url_for

from app.helpers.data import save_to_db
from tests.unittests.object_mother import ObjectMother
from tests.unittests.utils import OpenEventTestCase
from app import current_app as app
from app.helpers.flask_helpers import slugify

def get_event():
    event = ObjectMother.get_event()
    event.name = 'Super Event'
    event.start_time = datetime.now() + timedelta(days=5)
    event.end_time = event.start_time + timedelta(days=5)
    event.location_name = 'India'
    event.searchable_location_name = 'India'
    event.state = 'Published'
    return event

def get_event_two():
    event = get_event()
    event.start_time = datetime.now() + timedelta(days=8)
    event.end_time = event.start_time + timedelta(days=4)
    event.name = 'Random Event'
    return event

def assert_events(self, location_name, query_params_one=None, query_params_two=None):
    if query_params_two is None:
        query_params_two = {}
    if query_params_one is None:
        query_params_one = {}
    rv = self.app.get(url_for('explore.explore_view', location=slugify(location_name)) + '?' +
                      urllib.urlencode(query_params_one), follow_redirects=True)
    self.assertTrue("Super Event" in rv.data, msg=rv.data)
    self.assertTrue("Random Event" not in rv.data, msg=rv.data)
    rv = self.app.get(url_for('explore.explore_view', location=slugify(location_name)) + '?' +
                      urllib.urlencode(query_params_two), follow_redirects=True)
    self.assertTrue("Super Event" not in rv.data, msg=rv.data)
    self.assertTrue("Random Event" in rv.data, msg=rv.data)

class TestSearchEventPage(OpenEventTestCase):

    def test_location_filter(self):
        with app.test_request_context():
            event = get_event()
            save_to_db(event, "Event Saved")
            event = get_event_two()
            event.location_name = 'United States'
            event.searchable_location_name = 'United States'
            save_to_db(event, "Event Saved")
            rv = self.app.get(url_for('explore.explore_view', location=slugify('India')), follow_redirects=True)
            self.assertTrue("Super Event" in rv.data, msg=rv.data)
            self.assertTrue("Random Event" not in rv.data, msg=rv.data)
            rv = self.app.get(url_for('explore.explore_view', location=slugify('United States')), follow_redirects=True)
            self.assertTrue("Super Event" not in rv.data, msg=rv.data)
            self.assertTrue("Random Event" in rv.data, msg=rv.data)

    def test_topic_filter(self):
        with app.test_request_context():
            event_one = get_event()
            save_to_db(event_one, "Event Saved")
            event_two = get_event_two()
            event_two.topic = 'Home & Lifestyle'
            event_two.sub_topic = 'Home & Garden'
            save_to_db(event_two, "Event Saved")

            query_params_one = {
                'category': event_one.topic
            }
            query_params_two = {
                'category': event_two.topic
            }
            assert_events(self, event_one.location_name, query_params_one, query_params_two)

    def test_sub_topic_filter(self):
        with app.test_request_context():
            event_one = get_event()
            save_to_db(event_one, "Event Saved")
            event_two = get_event_two()
            event_two.topic = 'Home & Lifestyle'
            event_two.sub_topic = 'Home & Garden'
            save_to_db(event_two, "Event Saved")

            query_params_one = {
                'category': event_one.topic,
                'sub-category': event_one.sub_topic
            }
            query_params_two = {
                'category': event_two.topic,
                'sub-category': event_two.sub_topic
            }
            assert_events(self, event_one.location_name, query_params_one, query_params_two)

    def test_type_filter(self):
        with app.test_request_context():
            event_one = get_event()
            save_to_db(event_one, "Event Saved")
            event_two = get_event_two()
            event_two.type = 'Appearance or Signing'
            save_to_db(event_two, "Event Saved")

            query_params_one = {
                'type': event_one.type,
            }
            query_params_two = {
                'type': event_two.type
            }
            assert_events(self, event_one.location_name, query_params_one, query_params_two)

    def test_custom_date_range_filter(self):
        with app.test_request_context():
            event_one = get_event()
            save_to_db(event_one, "Event Saved")
            event_two = get_event_two()
            save_to_db(event_two, "Event Saved")

            query_params_one = {
                'period': (event_one.start_time - timedelta(days=1)).strftime('%m-%d-%Y') + ' to ' +
                          (event_one.end_time + timedelta(days=1)).strftime('%m-%d-%Y')
            }
            query_params_two = {
                'period': (event_two.start_time - timedelta(days=1)).strftime('%m-%d-%Y') + ' to ' +
                          (event_two.end_time + timedelta(days=1)).strftime('%m-%d-%Y')
            }
            assert_events(self, event_one.location_name, query_params_one, query_params_two)

if __name__ == '__main__':
    unittest.main()

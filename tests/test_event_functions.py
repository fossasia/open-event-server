import unittest

from tests.auth_helper import register, login
from tests.utils import OpenEventTestCase
from tests.setup_database import Setup
from tests.object_mother import ObjectMother
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.helpers.data_getter import DataGetter
from flask import url_for


class TestEventFunctions(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_add_event_to_db(self):
        event = ObjectMother.get_event()
        with app.test_request_context():
            save_to_db(event, "Event saved")
            self.assertEqual(event.id, event.id)

    def test_event_publish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            save_to_db(event, "Event saved")
            url = url_for('events.publish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Published", event.state, msg=event.state)

    def test_event_unpublish(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.state = "Published"
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            save_to_db(event, "Event saved")
            url = url_for('events.unpublish_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            event = DataGetter.get_event(event.id)
            self.assertEqual("Draft", event.state, msg=event.state)

    def test_event_delete(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            save_to_db(event, "Event saved")
            url = url_for('events.delete_view', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Forbidden" in rv.data, msg=rv.data)

    def test_event_copy(self):
        with app.test_request_context():
            event = ObjectMother.get_event()
            register(self.app, u'email2@gmail.com', u'test2')
            login(self.app, 'email2@gmail.com', 'test2')
            save_to_db(event, "Event saved")
            url = url_for('events.copy_event', event_id=event.id)
            rv = self.app.get(url, follow_redirects=True)
            self.assertTrue("Copy of event1" in rv.data, msg=rv.data)

if __name__ == '__main__':
    unittest.main()

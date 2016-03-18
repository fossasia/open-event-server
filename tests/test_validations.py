import unittest
from tests.setup import Setup
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from mock import MagicMock
from open_event.helpers.validators import CustomDateEventValidate, CustomDateSessionValidate
from open_event.forms.admin.event_form import EventForm
from open_event.forms.admin.session_form import SessionForm
from datetime import datetime
from wtforms import ValidationError
from open_event.models.event import Event
from flask import request


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event = Event(name="event1",
                          start_time=datetime(2013, 8, 4, 12, 30, 45),
                          end_time=datetime(2016, 9, 4, 12, 30, 45))
            event.owner = 1
            save_to_db(event, "Event saved")

            self.event_form = EventForm()
            self.session_form = SessionForm()

    def tearDown(self):
        Setup.drop_db()

    def test_event_end_time_smaller_than_start_time(self):
        with app.test_request_context():
            self.event_form['start_time'].data = MagicMock(return_value=datetime(2015, 8, 4, 12, 30, 45))
            self.event_form['end_time'].data = MagicMock(return_value=datetime(2015, 1, 4, 12, 30, 45))
            self.assertRaises(ValidationError, CustomDateEventValidate().__call__(form=self.event_form, field=None))

    def test_event_start_time_smaller_than_end_time(self):
        with app.test_request_context():
            self.event_form['start_time'].data = MagicMock(return_value=datetime(2015, 8, 4, 12, 30, 45))
            self.event_form['end_time'].data = MagicMock(return_value=datetime(2015, 9, 4, 12, 30, 45))
            self.assertRaises(ValidationError, CustomDateEventValidate().__call__(form=self.event_form, field=None))

    def test_session_start_time_and_end_time_contains_in_event_date(self):
        with app.test_request_context():
            self.session_form['start_time'].data = datetime(2013, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = datetime(2016, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            CustomDateSessionValidate().__call__(form=self.session_form, field=None)

    def test_session_end_time_greater_than_start_time(self):
        with app.test_request_context():
            self.session_form['start_time'].data = datetime(2015, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = datetime(2014, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            self.assertRaises(ValidationError, CustomDateSessionValidate().__call__(form=self.session_form, field=None))


if __name__ == '__main__':
    unittest.main()

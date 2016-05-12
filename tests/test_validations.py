from datetime import datetime
import unittest

from flask import request
from wtforms import ValidationError

from tests.utils import OpenEventTestCase
from tests.set_up import Setup
from open_event import current_app as app
from open_event.helpers.data import save_to_db
from open_event.helpers.validators import (
    CustomDateEventValidate,
    CustomDateSessionValidate,
)
from open_event.forms.admin.event_form import EventForm
from open_event.forms.admin.session_form import SessionForm
from open_event.models.event import Event


class TestValidation(OpenEventTestCase):
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

    def test_event_start_and_end_time(self):
        """Event end time should not be smaller than its start time"""
        with app.test_request_context():
            self.event_form['start_time'].data = \
                datetime(2015, 8, 4, 12, 30, 45)
            self.event_form['end_time'].data = \
                datetime(2015, 1, 4, 12, 30, 45)
            with self.assertRaises(ValidationError):
                CustomDateEventValidate().__call__(form=self.event_form,
                                                   field=None)

    def test_session_end_time_range(self):
        """Session end time should be inside Event time range"""
        with app.test_request_context():
            self.session_form['start_time'].data = \
                datetime(2013, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = \
                datetime(2017, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            with self.assertRaises(ValidationError):
                CustomDateSessionValidate().__call__(form=self.session_form,
                                                     field=None)

    def test_session_start_time_range(self):
        """Session start time should be inside Event time range"""
        with app.test_request_context():
            self.session_form['start_time'].data = \
                datetime(2012, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = \
                datetime(2016, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            with self.assertRaises(ValidationError):
                CustomDateSessionValidate().__call__(form=self.session_form,
                                                     field=None)

    def test_session_both_time_range(self):
        """Both Session start and end time should be inside Event time range
        """
        with app.test_request_context():
            self.session_form['start_time'].data = \
                datetime(2012, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = \
                datetime(2017, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            with self.assertRaises(ValidationError):
                CustomDateSessionValidate().__call__(form=self.session_form,
                                                     field=None)

    def test_session_start_and_end_time(self):
        """Session end time should not be smaller than its start time"""
        with app.test_request_context():
            self.session_form['start_time'].data = \
                datetime(2015, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = \
                datetime(2014, 9, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            with self.assertRaises(ValidationError):
                CustomDateSessionValidate().__call__(form=self.session_form,
                                                     field=None)

    def test_session_both_time_equality(self):
        """Session end time and start time should not be equal"""
        with app.test_request_context():
            self.session_form['start_time'].data = \
                datetime(2015, 8, 4, 12, 30, 45)
            self.session_form['end_time'].data = \
                datetime(2015, 8, 4, 12, 30, 45)
            request.url = 'http://0.0.0.0:5000/admin/event/1'
            with self.assertRaises(ValidationError):
                CustomDateSessionValidate().__call__(form=self.session_form,
                                                     field=None)

if __name__ == '__main__':
    unittest.main()

import unittest
from tests.setup import Setup
from open_event import app
from open_event.helpers.data import save_to_db
from tests.object_mother import ObjectMother
from mock import MagicMock
from open_event.helpers.validators import CustomDateEventValidate
from open_event.forms.admin.event_form import EventForm
from datetime import datetime
from wtforms import ValidationError
class TestValidation(unittest.TestCase):
    def setUp(self):
        self.app = Setup.create_app()
        with app.test_request_context():
            event = ObjectMother.get_event()
            event.owner = 1
            save_to_db(event,"Event saved")

            self.form = EventForm()

    def tearDown(self):
        Setup.drop_db()

    def test_event_end_time_smaller_than_start_time(self):
        self.form['start_time'].data = MagicMock(return_value=datetime(2015, 8, 4, 12, 30, 45))
        self.form['end_time'].data = MagicMock(return_value=datetime(2015, 1, 4, 12, 30, 45))
        self.assertRaises(ValidationError, CustomDateEventValidate().__call__(form=self.form, field=None))

    def test_event_start_time_smaller_than_end_time(self):
        self.form['start_time'].data = MagicMock(return_value=datetime(2015, 8, 4, 12, 30, 45))
        self.form['end_time'].data = MagicMock(return_value=datetime(2015, 9, 4, 12, 30, 45))
        self.assertRaises(ValidationError, CustomDateEventValidate().__call__(form=self.form, field=None))



if __name__ == '__main__':
    unittest.main()
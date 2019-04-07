import unittest
from datetime import datetime
from pytz import timezone

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.speakers_calls import SpeakersCallSchema
from app.factories.speakers_call import SpeakersCallFactory
from app.models import db
from app.api.helpers.db import save_to_db
from tests.all.integration.setup_database import Setup


class TestSpeakersCallValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_date_pass(self):
        """
        Speakers Call Validate Date - Tests if the function runs without an exception
        :return:
        """
        schema = SpeakersCallSchema()
        original_data = {
            'data': {}
        }
        data = {
            'starts_at': datetime(2003, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2003, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC'))
        }
        SpeakersCallSchema.validate_date(schema, data, original_data)

    def test_date_start_gt_end(self):
        """
        Speakers Call Validate Date - Tests if exception is raised when ends_at is before starts_at
        :return:
        """
        schema = SpeakersCallSchema()
        original_data = {
            'data': {}
        }
        data = {
            'starts_at': datetime(2003, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2003, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC'))
        }
        with self.assertRaises(UnprocessableEntity):
            SpeakersCallSchema.validate_date(schema, data, original_data)

    def test_date_db_populate(self):
        """
        Speakers Call Validate Date - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with app.test_request_context():
            schema = SpeakersCallSchema()
            obj = SpeakersCallFactory()
            save_to_db(obj)

            original_data = {
                'data': {
                    'id': 1
                }
            }
            data = {}
            SpeakersCallSchema.validate_date(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

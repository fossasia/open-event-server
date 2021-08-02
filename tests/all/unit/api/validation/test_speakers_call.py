import unittest
from datetime import datetime
from unittest import TestCase

from pytz import timezone

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.speakers_calls import SpeakersCallSchema


class TestSpeakersCallValidation(TestCase):
    def test_date_pass(self):
        """
        Speakers Call Validate Date - Tests if the function runs without an exception
        :return:
        """
        schema = SpeakersCallSchema()
        original_data = {'data': {}}
        data = {
            'starts_at': datetime(2003, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2003, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'event_starts_at': datetime(2003, 9, 10, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
        }
        SpeakersCallSchema.validate_date(schema, data, original_data)

    def test_date_start_gt_end(self):
        """
        Speakers Call Validate Date - Tests if exception is raised when ends_at is before starts_at
        :return:
        """
        schema = SpeakersCallSchema()
        original_data = {'data': {}}
        data = {
            'starts_at': datetime(2003, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2003, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'event_starts_at': datetime(2003, 9, 10, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
        }
        with self.assertRaises(UnprocessableEntityError):
            SpeakersCallSchema.validate_date(schema, data, original_data)

    # def test_date_start_gt_event_end(self):
    #     """
    #     Speakers Call Validate Date-Tests if exception is raised when speakers_call starts_at is after event starts_at
    #     :return:
    #     """
    #     schema = SpeakersCallSchema()
    #     original_data = {
    #         'data': {}
    #     }
    #     data = {
    #         'starts_at': datetime(2003, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
    #         'ends_at': datetime(2003, 9, 10, 12, 30, 45).replace(tzinfo=timezone('UTC')),
    #         'event_starts_at': datetime(2003, 9, 2, 12, 30, 45).replace(tzinfo=timezone('UTC'))
    #     }
    #     with self.assertRaises(UnprocessableEntityError):
    #         SpeakersCallSchema.validate_date(schema, data, original_data)

    # def test_date_end_gt_event_end(self):
    #     """
    #     Speakers Call Validate Date-Tests if exception is raised when speakers_call ends_at is after event starts_at
    #     :return:
    #     """
    #     schema = SpeakersCallSchema()
    #     original_data = {
    #         'data': {}
    #     }
    #     data = {
    #         'starts_at': datetime(2003, 9, 2, 12, 30, 45).replace(tzinfo=timezone('UTC')),
    #         'ends_at': datetime(2003, 9, 10, 12, 30, 45).replace(tzinfo=timezone('UTC')),
    #         'event_starts_at': datetime(2003, 9, 5, 12, 30, 45).replace(tzinfo=timezone('UTC'))
    #     }
    #     with self.assertRaises(UnprocessableEntityError):
    #         SpeakersCallSchema.validate_date(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

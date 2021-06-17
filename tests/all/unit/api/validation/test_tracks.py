import unittest
from unittest import TestCase

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.tracks import TrackSchema


class TestEventValidation(TestCase):
    def test_valid_color_pass(self):
        """
        Tracks Validate Color - Tests if the function runs without an exception
        :return:
        """
        schema = TrackSchema()
        data = {'color': '#1ded15'}
        TrackSchema.valid_color(schema, data)

    def test_not_valid_color(self):
        """
        Tracks Validate Color - Tests if exception is raised
        :return:
        """
        schema = TrackSchema()
        data = {'color': '12'}
        with self.assertRaises(UnprocessableEntityError):
            TrackSchema.valid_color(schema, data)


if __name__ == '__main__':
    unittest.main()

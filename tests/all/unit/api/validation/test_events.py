import unittest
from unittest import TestCase

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.events import EventSchemaPublic


class TestEventValidation(TestCase):
    def test_timezone_pass(self):
        """
        Events Validate Timezone - Tests if the function runs without an exception
        :return:
        """
        schema = EventSchemaPublic()
        original_data = {'data': {}}
        data = {'timezone': 'UTC'}
        EventSchemaPublic.validate_timezone(schema, data, original_data)

    def test_timezone_not_available(self):
        """
        Events Validate Timezone - Tests if exception is raised
        :return:
        """
        schema = EventSchemaPublic()
        original_data = {'data': {}}
        data = {'timezone': ''}
        with self.assertRaises(UnprocessableEntityError):
            EventSchemaPublic.validate_timezone(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

import unittest
from unittest import TestCase

from app.api.schema.session_types import SessionTypeSchema


class TestEventValidation(TestCase):
    def test_validate_length_pass(self):
        """
        Events Validate Timezone - Tests if the function runs without an exception
        :return:
        """
        schema = SessionTypeSchema()
        data = {'length': '12:23'}
        SessionTypeSchema.validate_length(schema, data)


if __name__ == '__main__':
    unittest.main()

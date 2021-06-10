import unittest
from unittest import TestCase

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.session_types import SessionTypeSchema


class TestSessionTypesValidation(TestCase):
    def test_validate_length_pass(self):
        """
        Session Types Validate length - Tests if the function runs without an exception
        :return:
        """
        schema = SessionTypeSchema()
        data = {'length': '12:23'}
        SessionTypeSchema.validate_length(schema, data)

    def test_validate_length_exception(self):
        """
        Session Types Validate length - Tests if exception is raised
        :return:
        """
        schema = SessionTypeSchema()
        data = {'length': '1223'}
        with self.assertRaises(UnprocessableEntityError):
            SessionTypeSchema.validate_length(schema, data)


if __name__ == '__main__':
    unittest.main()

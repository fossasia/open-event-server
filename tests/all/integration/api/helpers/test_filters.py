import unittest

from app import current_app as app
from app.api.helpers.filters import json_to_rest_filter_list
from tests.all.integration.utils import OpenEventTestCase
from tests.all.integration.setup_database import Setup


class TestFiltersHelperValidation(OpenEventTestCase):
    """Contains tests for filters helpers"""

    def setUp(self):
        self.app = Setup.create_app()

    def test_json_to_rest_filter_list(self):
        """
        Method to test that a json string is converted to a rest filter object
        list.
        """
        with app.test_request_context():
            json_string = """
            [
                {
                    "name1": "some event 1",
                    "op1": "operand 1",
                    "val1": "value for operand 1"
                },
                {
                    "op2": "operand 2",
                    "val2": "value for operand 2",
                    "name2": "some event 2"
                }
            ]
            """

            filter_list = json_to_rest_filter_list(json_string)

            # Test that the length of the list is correct.
            self.assertEqual(len(filter_list), 2)

            for i, fil in enumerate(filter_list):
                # Test that each of the tuples returned has the correct name type.
                self.assertEqual(type(fil).__name__, 'RestFilter')

                # Test that the current tuple has the correct fields.
                fields = fil._fields
                self.assertIn('name' + str(i + 1), fields)
                self.assertIn('op' + str(i + 1), fields)
                self.assertIn('val' + str(i + 1), fields)

                # Test that the value is correct for each of the fields, and
                # also that the fields are sorted. These tests will fail if
                # the fields aren't sorted.
                self.assertEqual(fil[0], 'some event ' + str(i + 1))
                self.assertEqual(fil[1], 'operand ' + str(i + 1))
                self.assertEqual(fil[2], 'value for operand ' + str(i + 1))


if __name__ == '__main__':
    unittest.main()

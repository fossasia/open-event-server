import unittest
import string
import datetime


from app.api.helpers.exceptions import UnprocessableEntity
from app.api.helpers.utilities import get_filename_from_cd
from app.api.helpers.utilities import string_empty, dasherize, represents_int, str_generator, \
                                      require_relationship, monthdelta


class TestUtilitiesHelperValidation(unittest.TestCase):
    def test_get_filename_from_cd(self):
        """Test the method get_filename_from_cd"""

        test_data_first = 'attachment; filename="image.png"'
        test_data_none = None
        expected_response_first = ('"image', '.png"')
        expected_response_none = ('', '')

        response_first = get_filename_from_cd(test_data_first)
        response_none = get_filename_from_cd(test_data_none)

        self.assertEqual(expected_response_first, response_first)
        self.assertEqual(expected_response_none, response_none)

    def test_dasherize(self):
        """Method to test whether an attribute dasherizes or not"""

        field = "starts_at"
        dasherized_field = "starts-at"
        result = dasherize(field)
        self.assertEqual(result, dasherized_field)

    def test_represents_int(self):
        """Method to test representation of int"""

        self.assertTrue(represents_int(4))
        self.assertFalse(represents_int('test'))


    def test_string_empty(self):
        """Method to test whether an empty string is correctly identified."""

        self.assertTrue(string_empty(''))
        self.assertTrue(string_empty(' '))
        self.assertTrue(string_empty('\t'))
        self.assertTrue(string_empty('\n'))
        self.assertFalse(string_empty(None))
        self.assertFalse(string_empty('some value'))
        self.assertFalse(string_empty('  some   value '))
        self.assertFalse(string_empty(0))
        self.assertFalse(string_empty([]))
        self.assertFalse(string_empty(False))

    def test_str_generator(self):
        """Method to test str_generator."""

        generated_string = str_generator()
        self.assertEqual(len(generated_string), 6)
        self.assertRegex(generated_string, r'^[A-Z0-9]+$')
        self.assertNotRegex(generated_string, r'^[a-z]+$')

        generated_string = str_generator(8, chars=string.ascii_lowercase)
        self.assertEqual(len(generated_string), 8)
        self.assertRegex(generated_string, r'^[a-z]+$')
        self.assertNotRegex(generated_string, r'^[A-Z0-9]+$')

        generated_string = str_generator(chars='ABC253')
        self.assertRegex(generated_string, r'^[ABC253]+$')

    def test_require_relationship(self):
        """Method to test relationship in request data"""

        with self.assertRaises(UnprocessableEntity):
            data = ['event']
            require_relationship(['sponsor', 'event'], data)

    def test_monthdelta(self):
        """Method to test difference in months result"""

        test_date = datetime.datetime(2000, 6, 18)
        test_future_date = monthdelta(test_date, 3)
        self.assertEqual(test_future_date, datetime.datetime(2000, 9, 18))


if __name__ == '__main__':
    unittest.main()

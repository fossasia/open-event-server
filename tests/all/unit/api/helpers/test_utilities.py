import unittest
from app.api.helpers.utilities import get_filename_from_cd


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


if __name__ == '__main__':
    unittest.main()

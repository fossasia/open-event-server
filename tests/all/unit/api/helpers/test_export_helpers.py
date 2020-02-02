import unittest
from collections import OrderedDict
from datetime import datetime

from app.api.helpers.export_helpers import (
    handle_unserializable_data,
    make_filename,
    sorted_dict,
)


class TestExportHelperValidation(unittest.TestCase):
    def test_sorted_dict(self):
        """Method to test sorting of a json (dict/list->dict) returns OrderedDict"""

        request_dictdata = {"twokey": 1, "keyone": 3}
        request_ordereddict_data = OrderedDict([('twokey', 1), ('keyone', 3)])
        request_list_data = [{"twokey": 1, "keyone": 3}, {"threekey": 0, "keytwo": 2}]

        expected_dictdata = OrderedDict([('keyone', 3), ('twokey', 1)])
        expected_ordereddict_data = OrderedDict([('keyone', 3), ('twokey', 1)])
        expected_list_data = [
            OrderedDict([('keyone', 3), ('twokey', 1)]),
            OrderedDict([('keytwo', 2), ('threekey', 0)]),
        ]

        response_dictdata = sorted_dict(request_dictdata)
        response_ordereddict_data = sorted_dict(request_ordereddict_data)
        response_list_data = sorted_dict(request_list_data)

        self.assertEqual(expected_dictdata, response_dictdata)
        self.assertEqual(expected_ordereddict_data, response_ordereddict_data)
        self.assertEqual(expected_list_data, response_list_data)

    def test_make_filename(self):
        """Method to test speaker image filename for export"""

        correct_data = 'correctfilename.png'
        correct_response = 'Correctfilename.Png'
        actual_response = make_filename(correct_data)
        self.assertEqual(correct_response, actual_response)

        data_with_lt = 'datawith<name.png'
        response_with_lt = 'DatawithName.Png'
        actual_response = make_filename(data_with_lt)
        self.assertEqual(response_with_lt, actual_response)

        data_with_gt = 'datawith>name.png'
        response_with_gt = 'DatawithName.Png'
        actual_response = make_filename(data_with_gt)
        self.assertEqual(response_with_gt, actual_response)

        data_with_colon = 'datawith:name.png'
        response_with_colon = 'DatawithName.Png'
        actual_response = make_filename(data_with_colon)
        self.assertEqual(response_with_colon, actual_response)

        data_with_doublequotes = 'datawith"quotes.png'
        response_with_doublequotes = 'DatawithQuotes.Png'
        actual_response = make_filename(data_with_doublequotes)
        self.assertEqual(response_with_doublequotes, actual_response)

        data_with_forwardslash = 'datawith/slash.png'
        response_with_forwardslash = 'DatawithSlash.Png'
        actual_response = make_filename(data_with_forwardslash)
        self.assertEqual(response_with_forwardslash, actual_response)

        data_with_backslash = 'datawith\\slash.png'
        response_with_backslash = 'DatawithSlash.Png'
        actual_response = make_filename(data_with_backslash)
        self.assertEqual(response_with_backslash, actual_response)

        data_with_verticalbar = 'datawith|bar.png'
        response_with_verticalbar = 'DatawithBar.Png'
        actual_response = make_filename(data_with_verticalbar)
        self.assertEqual(response_with_verticalbar, actual_response)

        data_with_questionmark = 'datawith?mark.png'
        response_with_questionmark = 'DatawithMark.Png'
        actual_response = make_filename(data_with_questionmark)
        self.assertEqual(response_with_questionmark, actual_response)

        data_with_star = 'datawith*operator.png'
        response_with_star = 'DatawithOperator.Png'
        actual_response = make_filename(data_with_star)
        self.assertEqual(response_with_star, actual_response)

        data_with_semicolon = 'datawith;semicolon.png'
        response_with_semicolon = 'DatawithSemicolon.Png'
        actual_response = make_filename(data_with_semicolon)
        self.assertEqual(response_with_semicolon, actual_response)

    def test_handle_unserializable_data(self):
        """
        Method to test Handling of objects which cannot be serialized by json.dumps()
        """
        query_correct = datetime(2006, 11, 21, 16, 30, 12, 841100)
        expected_response = '2006-11-21 16:30:12.841100'
        actual_response = handle_unserializable_data(query_correct)
        self.assertEqual(expected_response, actual_response)

        query_incorrect = ['sample', 'data', 'incorrect']
        expected_response = None
        actual_response = handle_unserializable_data(query_incorrect)
        self.assertEqual(expected_response, actual_response)


if __name__ == '__main__':
    unittest.main()

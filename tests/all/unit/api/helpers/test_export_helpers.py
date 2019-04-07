import unittest

from collections import OrderedDict
from app.api.helpers.export_helpers import sorted_dict


class TestExportHelperValidation(unittest.TestCase):

    def test_sorted_dict(self):
        """Method to test sorting of a json (dict/list->dict) returns OrderedDict"""

        request_dictdata = {"twokey": 1, "keyone": 3}
        request_ordereddict_data = OrderedDict([('twokey', 1), ('keyone', 3)])
        request_list_data = [{"twokey": 1, "keyone": 3},
                             {"threekey": 0, "keytwo": 2}]

        expected_dictdata = OrderedDict(
            [('keyone', 3), ('twokey', 1)])
        expected_ordereddict_data = OrderedDict([('keyone', 3), ('twokey', 1)])
        expected_list_data = [OrderedDict([('keyone', 3), ('twokey', 1)]), OrderedDict([
            ('keytwo', 2), ('threekey', 0)])]

        response_dictdata = sorted_dict(request_dictdata)
        response_ordereddict_data = sorted_dict(request_ordereddict_data)
        response_list_data = sorted_dict(request_list_data)

        self.assertEqual(expected_dictdata, response_dictdata)
        self.assertEqual(expected_ordereddict_data, response_ordereddict_data)
        self.assertEqual(expected_list_data, response_list_data)


if __name__ == '__main__':
    unittest.main()

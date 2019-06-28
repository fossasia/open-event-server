import unittest

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.discount_codes import DiscountCodeSchemaTicket


class TestDiscountCodeValidation(OpenEventTestCase):

    def test_percent_value_lte_hundred(self):
        """
        Discount Code Validate Percentage Value - Tests if function runs without an exception
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {
            'data': {}
        }
        data = {
            'type': 'percent',
            'value': 90,
            'tickets': []
        }
        DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_percent_value_gt_hundred(self):
        """
        Discount Code Validate Percentage Value - Tests if exception is raised when percentage value is greater than 100
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {
            'data': {}
        }
        data = {
            'type': 'percent',
            'value': 110,
            'tickets': []
        }
        with self.assertRaises(UnprocessableEntity):
            DiscountCodeSchemaTicket.validate_value(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

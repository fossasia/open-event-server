import unittest
from datetime import datetime
from unittest import TestCase

from pytz import timezone

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.discount_codes import DiscountCodeSchemaTicket


class TestDiscountCodeValidation(TestCase):
    def test_quantity_pass(self):
        """
        Discount Code Validate Quantity - Tests if the function runs without an exception
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {'min_quantity': 10, 'max_quantity': 20, 'tickets_number': 30}
        DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_date_pass(self):
        """
        Discount Code Validate Date - Tests if the function runs without an exception
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {
            'valid_from': datetime(2099, 8, 4, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
            'valid_till': datetime(2099, 9, 4, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
        }
        DiscountCodeSchemaTicket.validate_date(schema, data, original_data)

    def test_date_start_gt_end(self):
        """
        Discount Code Validate Date - Tests if exception is raised when ends_at is before starts_at
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {
            'valid_from': datetime(2099, 9, 4, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
            'valid_till': datetime(2099, 8, 4, 12, 30, 45).replace(
                tzinfo=timezone('UTC')
            ),
        }
        with self.assertRaises(UnprocessableEntityError):
            DiscountCodeSchemaTicket.validate_date(schema, data, original_data)

    def test_quantity_min_gt_max(self):
        """
        Discount Code Validate Quantity - Tests if exception is raised when min_quantity greater than max
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {'min_quantity': 20, 'max_quantity': 10, 'tickets_number': 30}
        with self.assertRaises(UnprocessableEntityError):
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_quantity_max_gt_tickets_number(self):
        """
        Discount Code Validate Quantity - Tests if exception is raised when max_quantity greater than ticket_number
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {'min_quantity': 10, 'max_quantity': 30, 'tickets_number': 20}
        with self.assertRaises(UnprocessableEntityError):
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_percent_value_lte_hundred(self):
        """
        Discount Code Validate Percentage Value - Tests if function runs without an exception
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {'type': 'percent', 'value': 90, 'tickets': []}
        DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_percent_value_gt_hundred(self):
        """
        Discount Code Validate Percentage Value - Tests if exception is raised when percentage value is greater than 100
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {'data': {}}
        data = {'type': 'percent', 'value': 110, 'tickets': []}
        with self.assertRaises(UnprocessableEntityError):
            DiscountCodeSchemaTicket.validate_value(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

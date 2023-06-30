import unittest

import pytest

from app.api.helpers.errors import UnprocessableEntityError
from app.api.schema.discount_codes import DiscountCodeSchemaTicket
from tests.all.integration.utils import OpenEventLegacyTestCase
from tests.factories.discount_code import DiscountCodeFactory
from tests.factories.ticket import TicketFactory


class TestDiscountCodeValidation(OpenEventLegacyTestCase):
    def test_amount_lte_ticket_price(self):
        """
        Discount Code Validate Amount Value - Tests if function runs without an exception
        :return:
        """
        with self.app.test_request_context():
            TicketFactory(price=100)

            schema = DiscountCodeSchemaTicket()
            original_data = {'data': {}}
            data = {'type': 'amount', 'value': 70, 'tickets': ['1']}
            DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_amount_gt_ticket_price(self):
        """
        Discount Code Validate Amount Value - Tests if exception is raised when discount value is gt ticket price
        :return:
        """
        with self.app.test_request_context():
            TicketFactory(price=100)

            schema = DiscountCodeSchemaTicket()
            original_data = {'data': {}}
            data = {'type': 'amount', 'value': 150, 'tickets': ['1']}
            with pytest.raises(UnprocessableEntityError):
                DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_free_ticket(self):
        """
        Discount Code Validate Amount Value - Tests exception when discount code is created for free ticket
        :return:
        """
        with self.app.test_request_context():
            TicketFactory(price=0)

            schema = DiscountCodeSchemaTicket()
            original_data = {'data': {}}
            data = {'type': 'amount', 'value': 150, 'tickets': ['1']}
            with pytest.raises(UnprocessableEntityError):
                DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_quantity_db_populate(self):
        """
        Discount Code Validate Quantity - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with self.app.test_request_context():
            schema = DiscountCodeSchemaTicket()
            DiscountCodeFactory()

            original_data = {'data': {'id': 1}}
            data = {}
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

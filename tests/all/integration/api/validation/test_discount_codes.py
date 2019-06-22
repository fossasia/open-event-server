import unittest

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.discount_codes import DiscountCodeSchemaTicket
from app.api.helpers.db import save_to_db
from app.factories.discount_code import DiscountCodeFactory
from app.factories.ticket import TicketFactory
from tests.all.integration.setup_database import Setup


class TestDiscountCodeValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_quantity_pass(self):
        """
        Discount Code Validate Quantity - Tests if the function runs without an exception
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 10,
            'max_quantity': 20,
            'tickets_number': 30
        }
        DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_quantity_min_gt_max(self):
        """
        Discount Code Validate Quantity - Tests if exception is raised when min_quantity greater than max
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 20,
            'max_quantity': 10,
            'tickets_number': 30
        }
        with self.assertRaises(UnprocessableEntity):
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_quantity_max_gt_tickets_number(self):
        """
        Discount Code Validate Quantity - Tests if exception is raised when max_quantity greater than ticket_number
        :return:
        """
        schema = DiscountCodeSchemaTicket()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 10,
            'max_quantity': 30,
            'tickets_number': 20
        }
        with self.assertRaises(UnprocessableEntity):
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)

    def test_amount_lte_ticket_price(self):
        """
        Discount Code Validate Amount Value - Tests if function runs without an exception
        :return:
        """
        with app.test_request_context():
            ticket = TicketFactory()
            ticket.price = 100
            save_to_db(ticket)

            schema = DiscountCodeSchemaTicket()
            original_data = {
                'data': {}
            }
            data = {
                'type': 'amount',
                'value': 70,
                'tickets': ['1']
            }
            DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_amount_gt_ticket_price(self):
        """
        Discount Code Validate Amount Value - Tests if exception is raised when discount value is gt ticket price
        :return:
        """
        with app.test_request_context():
            ticket = TicketFactory()
            ticket.price = 100
            save_to_db(ticket)

            schema = DiscountCodeSchemaTicket()
            original_data = {
                'data': {}
            }
            data = {
                'type': 'amount',
                'value': 150,
                'tickets': ['1']
            }
            with self.assertRaises(UnprocessableEntity):
                DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_free_ticket(self):
        """
        Discount Code Validate Amount Value - Tests exception when discount code is created for free ticket
        :return:
        """
        with app.test_request_context():
            ticket = TicketFactory()
            ticket.price = 0
            save_to_db(ticket)

            schema = DiscountCodeSchemaTicket()
            original_data = {
                'data': {}
            }
            data = {
                'type': 'amount',
                'value': 150,
                'tickets': ['1']
            }
            with self.assertRaises(UnprocessableEntity):
                DiscountCodeSchemaTicket.validate_value(schema, data, original_data)

    def test_quantity_db_populate(self):
        """
        Discount Code Validate Quantity - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with app.test_request_context():
            schema = DiscountCodeSchemaTicket()
            obj = DiscountCodeFactory()
            save_to_db(obj)

            original_data = {
                'data': {
                    'id': 1
                }
            }
            data = {}
            DiscountCodeSchemaTicket.validate_quantity(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

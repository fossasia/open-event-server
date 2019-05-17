import unittest

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.access_codes import AccessCodeSchema
from app.factories.access_code import AccessCodeFactory
from app.api.helpers.db import save_to_db
from tests.all.integration.setup_database import Setup
import datetime

class TestAccessCodeValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_quantity_pass(self):
        """
        Acces Code Validate Quantity - Tests if the function runs without an exception
        :return:
        """
        schema = AccessCodeSchema()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 5,
            'max_quantity': 10,
            'tickets_number': 30
        }
        AccessCodeSchema.validate_order_quantity(schema, data, original_data)

    def test_quantity_min_gt_max(self):
        """
        Acces Code Validate Quantity - Tests if the exception is raised when min tickets > max tickets
        :return:
        """
        schema = AccessCodeSchema()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 10,
            'max_quantity': 5,
            'tickets_number': 30
        }
        with self.assertRaises(UnprocessableEntity):
            AccessCodeSchema.validate_order_quantity(schema, data, original_data)

    def test_quantity_max_gt_ticket(self):
        """
        Acces Code Validate Quantity - Tests if the exception is raised when max_quantity greater than ticket_number
        :return:
        """
        schema = AccessCodeSchema()
        original_data = {
            'data': {}
        }
        data = {
            'min_quantity': 10,
            'max_quantity': 20,
            'tickets_number': 15
        }
        with self.assertRaises(UnprocessableEntity):
            AccessCodeSchema.validate_order_quantity(schema, data, original_data)

    def test_date_valid_from_gt_valid_till(self):
        """
        Acces Code Validate Date - Tests if the exception is raised when valid_from is greater than valid_till
        :return:
        """
        schema = AccessCodeSchema()
        original_data = {
            'data': {}
        }
        data = {
            'valid_from': datetime.datetime(2019, 1, 1),
            'valid_till': datetime.datetime(2018, 1, 1)
        }
        with self.assertRaises(UnprocessableEntity):
            AccessCodeSchema.validate_date(schema, data, original_data)

    def test_date_pass(self):
        """
        Acces Code Validate Date - Tests if the date function runs without exception
        :return:
        """
        schema = AccessCodeSchema()
        original_data = {
            'data': {}
        }
        data = {
            'valid_from': datetime.datetime(2018, 1, 1),
            'valid_till': datetime.datetime(2019, 1, 1)
        }
        AccessCodeSchema.validate_date(schema, data, original_data)

    def test_quantity_db_populate(self):
        """
        Acces Code Validate Quantity - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with app.test_request_context():
            schema = AccessCodeSchema()
            obj = AccessCodeFactory()
            save_to_db(obj)

            original_data = {
                'data': {
                    'id': 1
                }
            }
            data = {}
            AccessCodeSchema.validate_order_quantity(schema, data, original_data)


if __name__ == "__main__":
    unittest.main()

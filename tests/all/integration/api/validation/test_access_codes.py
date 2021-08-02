import unittest

from app.api.schema.access_codes import AccessCodeSchema
from tests.all.integration.utils import OpenEventTestCase
from tests.factories.access_code import AccessCodeFactory


class TestAccessCodeValidation(OpenEventTestCase):
    def test_quantity_db_populate(self):
        """
        Acces Code Validate Quantity - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with self.app.test_request_context():
            schema = AccessCodeSchema()
            AccessCodeFactory()

            original_data = {'data': {'id': 1}}
            data = {}
            AccessCodeSchema.validate_order_quantity(schema, data, original_data)


if __name__ == "__main__":
    unittest.main()

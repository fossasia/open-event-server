import unittest
from datetime import datetime
from pytz import timezone

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.tickets import TicketSchema
from app.factories.ticket import TicketFactory


class TestTicketValidation(OpenEventTestCase):
    def test_date_db_populate(self):
        """
        Tickets Validate Date - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with self.app.test_request_context():
            schema = TicketSchema()
            TicketFactory()

            original_data = {'data': {'id': 1}}
            data = {}
            TicketSchema.validate_date(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

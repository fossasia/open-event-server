import unittest
from datetime import datetime
from pytz import timezone

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.sessions import SessionSchema
from app.factories.session import SessionFactory


class TestSessionValidation(OpenEventTestCase):
    def test_date_db_populate(self):
        """
        Sessions Validate Date - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with self.app.test_request_context():
            schema = SessionSchema()
            SessionFactory()

            original_data = {'data': {'id': 1}}
            data = {}
            SessionSchema.validate_fields(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

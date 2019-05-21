import unittest
from datetime import datetime
from pytz import timezone

from app import current_app as app
from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity
from app.api.schema.sessions import SessionSchema
from app.factories.session import SessionFactory
from app.models import db
from app.api.helpers.db import save_to_db
from tests.all.integration.setup_database import Setup


class TestSessionValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_date_pass(self):
        """
        Sessions Validate Date - Tests if the function runs without an exception
        :return:
        """
        schema = SessionSchema()
        original_data = {
            'data': {}
        }
        data = {
            'starts_at': datetime(2099, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2099, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC'))
        }
        SessionSchema.validate_date(schema, data, original_data)

    def test_date_start_gt_end(self):
        """
        Sessions Validate Date - Tests if exception is raised when ends_at is before starts_at
        :return:
        """
        schema = SessionSchema()
        original_data = {
            'data': {}
        }
        data = {
            'starts_at': datetime(2099, 9, 4, 12, 30, 45).replace(tzinfo=timezone('UTC')),
            'ends_at': datetime(2099, 8, 4, 12, 30, 45).replace(tzinfo=timezone('UTC'))
        }
        with self.assertRaises(UnprocessableEntity):
            SessionSchema.validate_date(schema, data, original_data)

    def test_date_db_populate(self):
        """
        Sessions Validate Date - Tests if validation works on values stored in db and not given in 'data'
        :return:
        """
        with app.test_request_context():
            schema = SessionSchema()
            obj = SessionFactory()
            save_to_db(obj)

            original_data = {
                'data': {
                    'id': 1
                }
            }
            data = {}
            SessionSchema.validate_date(schema, data, original_data)


if __name__ == '__main__':
    unittest.main()

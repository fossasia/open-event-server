import unittest

from app import current_app as app
from app.api.helpers.exceptions import UnprocessableEntity
from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.utilities import dasherize, require_relationship
from tests.unittests.setup_database import Setup


class TestUtilitiesHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_dasherize(self):
        """Method to test whether an attribute dasherizes or not"""

        with app.test_request_context():
            field = "starts_at"
            dasherized_field = "starts-at"
            result = dasherize(field)
            self.assertEqual(result, dasherized_field)

    def test_require_relationship(self):
        """Method to test relationship in request data"""

        with self.assertRaises(UnprocessableEntity):
            data = ['event']
            require_relationship(['sponsor', 'event'], data)


if __name__ == '__main__':
    unittest.main()

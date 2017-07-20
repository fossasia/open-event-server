import unittest

from app import current_app as app
from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.utilities import dasherize
from tests.unittests.setup_database import Setup


class TestUtilitiesHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_utlities(self):
        with app.test_request_context():
            field = "starts_at"
            dasherized_field = "starts-at"
            result = dasherize(field)
            self.assertEqual(result, dasherized_field)


if __name__ == '__main__':
    unittest.main()

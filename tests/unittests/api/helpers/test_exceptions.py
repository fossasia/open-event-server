import unittest

from tests.unittests.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity, ConflictException
from tests.unittests.setup_database import Setup


class TestExceptionsHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_exceptions(self):
        # Unprocessable Entity Exception
        with self.assertRaises(UnprocessableEntity):
            raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                      "min-quantity should be less than max-quantity")

        # Conflict Exception
        with self.assertRaises(ConflictException):
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")


if __name__ == '__main__':
    unittest.main()

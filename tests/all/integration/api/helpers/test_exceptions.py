import unittest

from tests.all.integration.utils import OpenEventTestCase
from app.api.helpers.exceptions import UnprocessableEntity, ConflictException, ForbiddenException, MethodNotAllowed
from tests.all.integration.setup_database import Setup


class TestExceptionsHelperValidation(OpenEventTestCase):
    def setUp(self):
        self.app = Setup.create_app()

    def test_exceptions(self):
        """Method to test all exceptions."""

        # Unprocessable Entity Exception
        with self.assertRaises(UnprocessableEntity):
            raise UnprocessableEntity({'pointer': '/data/attributes/min-quantity'},
                                      "min-quantity should be less than max-quantity")

        # Conflict Exception
        with self.assertRaises(ConflictException):
            raise ConflictException({'pointer': '/data/attributes/email'}, "Email already exists")

        # Forbidden Exception
        with self.assertRaises(ForbiddenException):
            raise ForbiddenException({'source': ''}, "Access Forbidden")

        # Method Not Allowed Exception
        with self.assertRaises(MethodNotAllowed):
            raise MethodNotAllowed({'source': ''}, "Method Not Allowed")


if __name__ == '__main__':
    unittest.main()

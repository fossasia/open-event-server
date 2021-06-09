import unittest
from unittest import TestCase

from app.api.helpers.errors import (
    BadRequestError,
    ConflictError,
    ForbiddenError,
    MethodNotAllowed,
    NotFoundError,
    ServerError,
    UnprocessableEntityError,
)


class TestExceptionsHelperValidation(TestCase):
    def test_exceptions(self):
        """Method to test all exceptions."""

        # Unprocessable Entity Exception
        with self.assertRaises(UnprocessableEntityError):
            raise UnprocessableEntityError(
                {'pointer': '/data/attributes/min-quantity'},
                "min-quantity should be less than max-quantity",
            )

        # Conflict Exception
        with self.assertRaises(ConflictError):
            raise ConflictError(
                {'pointer': '/data/attributes/email'}, "Email already exists"
            )

        # Forbidden Exception
        with self.assertRaises(ForbiddenError):
            raise ForbiddenError({'source': ''}, "Access Forbidden")

        # Not Found Error
        with self.assertRaises(NotFoundError):
            raise NotFoundError({'source': ''}, "Not Found")

        # Server Error
        with self.assertRaises(ServerError):
            raise ServerError({'source': ''}, "Internal Server Error")

        # Bad Request Error
        with self.assertRaises(BadRequestError):
            raise BadRequestError({'source': ''}, "Bad Request")

        # Method Not Allowed Exception
        with self.assertRaises(MethodNotAllowed):
            raise MethodNotAllowed({'source': ''}, "Method Not Allowed")


if __name__ == '__main__':
    unittest.main()

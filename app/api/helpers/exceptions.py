from .errors import ErrorResponse


# TODO(Areeb): Remove these duplicate errors


class UnprocessableEntity(ErrorResponse):
    """
    Default class for 422 Error
    """

    title = "Unprocessable Entity"
    status = 422


class ConflictException(ErrorResponse):
    """
    Default class for 409 Error
    """

    title = "Conflict"
    status = 409


class ForbiddenException(ErrorResponse):
    """
    Default class for 403 Error
    """

    title = 'Access Forbidden'
    status = 403


class MethodNotAllowed(ErrorResponse):
    """
    Default Class to throw HTTP 405 Exception
    """

    title = "Method Not Allowed"
    status = 405

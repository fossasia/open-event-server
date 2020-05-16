from .errors import ErrorResponse





class ConflictException(ErrorResponse):
    """
    Default class for 409 Error
    """

    title = "Conflict"
    status = 409





class MethodNotAllowed(ErrorResponse):
    """
    Default Class to throw HTTP 405 Exception
    """

    title = "Method Not Allowed"
    status = 405

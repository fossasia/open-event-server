from flask_rest_jsonapi.exceptions import JsonApiException


class UnprocessableEntity(JsonApiException):
    """
    Default class for 422 Error
    """
    title = "Unprocessable Entity"
    status = 422


class ConflictException(JsonApiException):
    """
    Default class for 409 Error
    """
    title = "Conflict"
    status = 409


class ForbiddenException(JsonApiException):
    """
    Default class for 403 Error
    """
    title = 'Access Forbidden'
    status = 403


class MethodNotAllowed(JsonApiException):
    """
    Default Class to throw HTTP 405 Exception
    """
    title = "Method Not Allowed"
    status = 405

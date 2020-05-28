import json
from typing import Union

from flask import make_response
from flask_rest_jsonapi import JsonApiException
from flask_rest_jsonapi.errors import jsonapi_errors


class ErrorResponse(JsonApiException):
    """
    Parent ErrorResponse class for handling json-api compliant errors.
    Inspired by the JsonApiException class of `flask-rest-jsonapi` itself
    """

    headers = {'Content-Type': 'application/vnd.api+json'}

    def __init__(self, source: Union[dict, str], detail=None, title=None, status=None):
        """Initialize a jsonapi ErrorResponse Object

        :param dict source: the source of the error
        :param str detail: the detail of the error
        """

        if isinstance(source, str) and detail is None:
            # We have been passed a single argument, and hence source is unknown
            # so we'll represent source as detail
            super().__init__(None, source)
        else:
            super().__init__(source, detail, title, status)

    def respond(self):
        """
        :return: a jsonapi compliant response object
        """
        dict_ = self.to_dict()
        return make_response(
            json.dumps(jsonapi_errors([dict_])), self.status, self.headers
        )


class ForbiddenError(ErrorResponse):
    """
    Default class for 403 Error
    """

    title = 'Access Forbidden'
    status = 403


class NotFoundError(ErrorResponse):
    """
    Default class for 404 Error
    """

    title = 'Not Found'
    status = 404


class ServerError(ErrorResponse):
    status = 500
    title = 'Internal Server Error'


class UnprocessableEntityError(ErrorResponse):
    """
    Default class for 422 Error
    """

    status = 422
    title = 'Unprocessable Entity'


class BadRequestError(ErrorResponse):
    """
    Default class for 400 Error
    """

    status = 400
    title = 'Bad Request'


class ConflictError(ErrorResponse):
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

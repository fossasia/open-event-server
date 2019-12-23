import json

from flask import make_response
from flask_rest_jsonapi.errors import jsonapi_errors


class ErrorResponse:
    """
    Parent ErrorResponse class for handling json-api compliant errors.
    Inspired by the JsonApiException class of `flask-rest-jsonapi` itself
    """
    title = 'Unknown error'
    status = 500
    headers = {'Content-Type': 'application/vnd.api+json'}

    def __init__(self, source, detail, title=None, status=None):
        """Initialize a jsonapi ErrorResponse Object

        :param dict source: the source of the error
        :param str detail: the detail of the error
        """
        self.source = source
        self.detail = detail
        if title is not None:
            self.title = title
        if status is not None:
            self.status = status

    def respond(self):
        """
        :return: a jsonapi compliant response object
        """
        dict_ = self.to_dict()
        return make_response(json.dumps(jsonapi_errors([dict_])), self.status, self.headers)

    def to_dict(self):
        """
        :return: Dict from details of the object
        """
        return {'status': self.status,
                'source': self.source,
                'title': self.title,
                'detail': self.detail}


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

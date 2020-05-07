from app.api.helpers.errors import (
    BadRequestError,
    ErrorResponse,
    ForbiddenError,
    NotFoundError,
    ServerError,
    UnprocessableEntityError,
)


def test_error_response_dict_details():
    """To test details in the form of dict"""
    error_response = ErrorResponse(source="test source", detail="test detail")
    expected_dict = {
        'status': error_response.status,
        'source': error_response.source,
        'title': error_response.title,
        'detail': error_response.detail,
    }
    assert error_response.to_dict() == expected_dict


def test_errors():
    """Method to test the status code of all errors"""
    forbidden_error = ForbiddenError({'source': ''}, 'Super admin access is required')
    assert forbidden_error.status == 403
    not_found_error = NotFoundError({'source': ''}, 'Object not found.')
    assert not_found_error.status == 404
    server_error = ServerError({'source': ''}, 'Internal Server Error')
    assert server_error.status == 500
    unprocessable_entity_error = UnprocessableEntityError(
        {'source': ''}, 'Entity cannot be processed'
    )
    assert unprocessable_entity_error.status == 422
    bad_request_error = BadRequestError({'source': ''}, 'Request cannot be served')
    assert bad_request_error.status == 400

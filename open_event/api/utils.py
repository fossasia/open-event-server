from flask_restplus import Model, fields, reqparse

# Parameters for a paginated response
PAGE_PARAMS = {
    'start': {'description': 'ID to begin from', 'type': int},
    'limit': {'description': 'Number of results to be retrieved', 'type': int},
}

# Base Api Model for a paginated response
PAGINATED_MODEL = Model('PaginatedModel', {
    'start': fields.Integer,
    'limit': fields.Integer,
    'count': fields.Integer,
    'next': fields.String,
    'previous': fields.String
})


# Base class for Paginated Resource
class PaginatedResourceBase():
    """
    Paginated Resource Helper class
    This includes basic properties used in the class
    """
    parser = reqparse.RequestParser()
    parser.add_argument('start', type=int, default=1)
    parser.add_argument('limit', type=int, default=20)

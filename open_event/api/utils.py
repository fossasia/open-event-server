from flask_restplus import Model, fields, reqparse

DEFAULT_PAGE_START = 1
DEFAULT_PAGE_LIMIT = 20

# Parameters for a paginated response
PAGE_PARAMS = {
    'start': {
        'description': 'Serial number to start from',
        'type': int,
        'default': DEFAULT_PAGE_START
    },
    'limit': {
        'description': 'Limit on the number of results',
        'type': int,
        'default': DEFAULT_PAGE_LIMIT
    },
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
    parser.add_argument('start', type=int, default=DEFAULT_PAGE_START)
    parser.add_argument('limit', type=int, default=DEFAULT_PAGE_LIMIT)

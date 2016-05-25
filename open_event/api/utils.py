from flask_restplus import Model, fields, reqparse


# Base Api Model for a paged response
PAGED_MODEL = Model('PagedModel', {
    'start': fields.Integer,
    'limit': fields.Integer,
    'count': fields.Integer,
    'next': fields.String,
    'previous': fields.String
})

# Request parser for a pagination-type Resource
PAGE_REQPARSER = reqparse.RequestParser()
PAGE_REQPARSER.add_argument('start', type=int, default=1)
PAGE_REQPARSER.add_argument('limit', type=int, default=20)

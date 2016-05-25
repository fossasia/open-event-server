from flask_restplus import Model, fields


PAGED_MODEL = Model('PagedModel', {
    'start': fields.Integer,
    'limit': fields.Integer,
    'next': fields.Url(absolute=True),
    'previous': fields.Url(absolute=True)
})

from flask.ext.restplus import  Namespace, fields
from flask.ext.restplus.fields import Raw

api = Namespace('errors', description='Error Responses')


class NotFoundStatus(Raw):
    __schema_type__ = 'string'
    __schema_example__ = 'NOT_FOUND'


class NotAuthorizedStatus(Raw):
    __schema_type__ = 'string'
    __schema_example__ = 'NOT_AUTHORIZED'


class ValidationStatus(Raw):
    __schema_type__ = 'string'
    __schema_example__ = 'INVALID_FIELD'


class InvalidServiceStatus(Raw):
    __schema_type__ = 'string'
    __schema_example__ = 'INVALID_SERVICE'


class ServerStatus(Raw):
    __schema_type__ = 'string'
    __schema_example__ = 'SERVER_ERROR'


class NotFoundCode(Raw):
    __schema_type__ = 'integer'
    __schema_example__ = 404


class NotAuthorizedCode(Raw):
    __schema_type__ = 'integer'
    __schema_example__ = 401


class ValidationCode(Raw):
    __schema_type__ = 'integer'
    __schema_example__ = 400


class InvalidServiceCode(Raw):
    __schema_type__ = 'integer'
    __schema_example__ = 400


class ServerCode(Raw):
    __schema_type__ = 'integer'
    __schema_example__ = 500


notfound_error_model = api.model('NotFoundError', {
    'code': NotFoundCode,
    'message': fields.String,
    'status': NotFoundStatus,
    'field': fields.String,
})

notauthorized_error_model = api.model('NotAuthorizedError', {
    'code': NotAuthorizedCode,
    'message': fields.String,
    'status': NotAuthorizedStatus,
    'field': fields.String,
})

validation_error_model = api.model('ValidationError', {
    'code': ValidationCode,
    'message': fields.String,
    'status': ValidationStatus,
    'field': fields.String,
})

invalidservice_error_model = api.model('InvalidServiceError', {
    'code': InvalidServiceCode,
    'message': fields.String,
    'status': InvalidServiceStatus,
    'field': fields.String,
})

server_error_model = api.model('ServerError', {
    'code': ServerCode,
    'message': fields.String,
    'status': ServerStatus,
    'field': fields.String,
})

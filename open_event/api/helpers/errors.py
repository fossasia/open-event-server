class BaseError(Exception):
    """Base Error Class"""

    def __init__(self, code=400, message='', status='', field=None):
        Exception.__init__(self)
        self.code = code
        self.message = message
        self.status = status
        self.field = field

    def to_dict(self):
        return {'code': self.code,
                'message': self.message,
                'status': self.status,
                'field': self.field, }


class NotFoundError(BaseError):
    def __init__(self, message='Not found'):
        BaseError.__init__(self)
        self.code = 404
        self.message = message
        self.status = 'NOT_FOUND'


class NotAuthorizedError(BaseError):
    def __init__(self, message='Unauthorized'):
        BaseError.__init__(self)
        self.code = 401
        self.message = message
        self.status = 'NOT_AUTHORIZED'


class PermissionDeniedError(BaseError):
    def __init__(self, message='Permission denied'):
        BaseError.__init__(self)
        self.code = 403
        self.message = message
        self.status = 'PERMISSION_DENIED'


class ValidationError(BaseError):
    def __init__(self, field, message='Invalid field'):
        BaseError.__init__(self)
        self.code = 400
        self.message = message
        self.status = 'INVALID_FIELD'
        self.field = field


class InvalidServiceError(BaseError):
    def __init__(self, message='Service does not belong to event'):
        BaseError.__init__(self)
        self.code = 400
        self.message = message
        self.status = 'INVALID_SERVICE'


class ServerError(BaseError):
    def __init__(self, message='Internal server error'):
        BaseError.__init__(self)
        self.code = 500
        self.message = message
        self.status = 'SERVER_ERROR'

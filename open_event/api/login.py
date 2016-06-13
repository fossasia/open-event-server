import json
from flask.ext.restplus import Resource, Namespace
from flask_jwt import JWTError

from .helpers.errors import NotAuthorizedError
from .helpers import custom_fields as fields

api = Namespace('login', description='Login')

LOGIN = api.model('Login', {
    'email': fields.Email(required=True),
    'password': fields.String(required=True)
})

TOKEN = api.model('Token', {
    'access_token': fields.String()
})


@api.route('')
class Login(Resource):
    @api.doc('get_token')
    @api.expect(LOGIN)
    @api.marshal_with(TOKEN)
    @api.response(401, 'Authentication Failed')
    def post(self):
        from .. import jwt
        try:
            response = jwt.auth_request_callback()
            return json.loads(response.data)
        except JWTError as e:
            raise NotAuthorizedError(message='{}: {}'.format(e.error,
                                                             e.description))

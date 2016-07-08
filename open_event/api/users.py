from flask.ext.restplus import Resource, Namespace

from open_event.models.user import User as UserModel
from open_event.models.user_detail import UserDetail as UserDetailModel
from open_event.helpers.data import DataManager, record_activity

from .helpers.helpers import get_paginated_list, requires_auth
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, BaseDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('users', description='Users', path='/')


USER_DETAIL = api.model('UserDetail', {
    'fullname': fields.String(),
    'details': fields.String(),
    'avatar': fields.Upload(),
    'contact': fields.String(),
    'facebook': fields.String(),
    'twitter': fields.String()
})

USER = api.model('User', {
    'id': fields.Integer(),
    'email': fields.Email(required=True),
    'signup_time': fields.DateTime(),
    'last_access_time': fields.DateTime(),
    'user_detail': fields.Nested(USER_DETAIL)
})

USER_PAGINATED = api.clone('UserPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(USER))
})

USER_PUT = api.clone('UserPut', USER)
del USER_PUT['id']
del USER_PUT['signup_time']
del USER_PUT['last_access_time']

USER_POST = api.model('UserPost', {
    'email': fields.Email(required=True),
    'password': fields.String(required=True)
})

# Responses

USER_POST_RESPONSES = POST_RESPONSES.copy()
del USER_POST_RESPONSES[404]
del USER_POST_RESPONSES[401]


# DAO

class UserDetailDAO(BaseDAO):
    pass


class UserDAO(BaseDAO):
    def create(self, data):
        data = self.validate(data)
        user = DataManager.create_user([data['email'], data['password']])
        return user

    def update(self, id_, data):
        data = self.validate_put(data, self.put_api_model)
        user_detail = data.get('user_detail', {})
        del data['user_detail']
        item = BaseDAO.update(self, id_, data, validate=False)
        DetailDAO.update(item.user_detail.id, user_detail)
        return item


DAO = UserDAO(UserModel, USER_POST, USER_PUT)
DetailDAO = UserDetailDAO(UserDetailModel, USER_DETAIL)


@api.route('/users/<int:user_id>')
@api.response(404, 'User not found')
class User(Resource):
    @api.doc('get_user')
    @api.marshal_with(USER)
    def get(self, user_id):
        """Fetch a user given its id"""
        return DAO.get(user_id)

    @requires_auth
    @api.doc('delete_user')
    @api.marshal_with(USER)
    def delete(self, user_id):
        """Delete a user given its id"""
        return DAO.delete(user_id)

    @requires_auth
    @api.doc('update_user', responses=PUT_RESPONSES)
    @api.marshal_with(USER)
    @api.expect(USER_PUT)
    def put(self, user_id):
        """Update a user given its id"""
        user = DAO.update(user_id, self.api.payload)
        record_activity('update_user', user=user)
        return user


@api.route('/users')
class UserList(Resource):
    @api.doc('list_users')
    @api.marshal_list_with(USER)
    def get(self):
        """List all users"""
        return DAO.list()

    # @requires_auth
    @api.doc('create_user', responses=USER_POST_RESPONSES)
    @api.marshal_with(USER)
    @api.expect(USER_POST)
    def post(self):
        """Create a user"""
        return DAO.create(self.api.payload)


@api.route('/users/page')
class UserListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_users_paginated', params=PAGE_PARAMS)
    @api.marshal_with(USER_PAGINATED)
    def get(self):
        """List users in a paginated manner"""
        return get_paginated_list(
            UserModel,
            args=self.parser.parse_args()
        )

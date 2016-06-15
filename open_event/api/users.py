from flask.ext.restplus import Resource, Namespace

from open_event.models import user as UserModel
from open_event.models import user_detail as UserDetailModel

from .helpers.helpers import get_paginated_list, requires_auth
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, BaseDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('users', description='Users', path='/')


USER_DETAIL = api.model('UserDetail', {
    'fullname': fields.String(),
    'details': fields.String(),
    'avatar': fields.ImageUri(),
    'contact': fields.String(),
    'facebook': fields.String(),
    'twitter': fields.String()
})

USER = api.model('User', {
    'id': fields.Integer(),
    'email': fields.Email(required=True),
    'user_detail': fields.Nested(USER_DETAIL)
})


class UserDetailDAO(BaseDAO):
    pass


class UserDAO(BaseDAO):
    pass


DAO = UserDAO(UserModel)
DetailDAO = UserDetailDAO(UserDetailModel)

from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api
from app.api.users import UserList, UserDetail

api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)

# users
api.route(UserList, 'user_list', '/users')
api.route(UserDetail, 'user_detail', '/users/<int:id>')

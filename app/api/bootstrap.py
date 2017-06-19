from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api
from app.api.helpers.permission_manager import permission_manager

api_v1 = Blueprint('v1', __name__, url_prefix='/v1')
api = Api(app, api_v1)
api.permission_manager(permission_manager)

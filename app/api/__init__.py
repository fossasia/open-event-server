from flask import current_app as app, Blueprint
from flask_rest_jsonapi import Api

api_v1 = Blueprint('api', __name__, url_prefix='/v1')
api = Api(app, api_v1)

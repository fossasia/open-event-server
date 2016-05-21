from flask import Blueprint
from flask.ext.restplus import Api

from .events import api as event_api

api_v2 = Blueprint('api', __name__, url_prefix='/api/v2')

api = Api(api_v2, version='2.0', title='Organizer Server APIs',
    description='Open Event Organizer APIs',
)

api.add_namespace(event_api)

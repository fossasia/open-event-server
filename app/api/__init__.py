from flask import Blueprint, render_template
from flask.ext.restplus import Api
from flask_login import current_user

from helpers.error_docs import api as error_models
from helpers.errors import (
    NotFoundError,
    NotAuthorizedError,
    PermissionDeniedError,
    ValidationError,
    InvalidServiceError,
    ServerError,
)
from .attendees import api as attendees_api
from .events import api as event_api
from .exports import api as exports_api
from .extras import api as extras_api
from .imports import api as imports_api
from .login import api as login_api
from .microlocations import api as microlocation_api
from .notifications import api as notifications_api
from .sessions import api as session_api
from .speakers import api as speaker_api
from .sponsors import api as sponsor_api
from .tickets import api as tickets_apt
from .tracks import api as track_api
from .users import api as users_api

api_v1 = Blueprint('api', __name__, url_prefix='/api/v1')

api = Api(api_v1, version='1.0', title='Organizer Server APIs',
          description='Open Event Organizer APIs')

api.add_namespace(event_api)
api.add_namespace(session_api)
api.add_namespace(track_api)
api.add_namespace(speaker_api)
api.add_namespace(sponsor_api)
api.add_namespace(microlocation_api)
api.add_namespace(login_api)
api.add_namespace(exports_api)
api.add_namespace(imports_api)
api.add_namespace(users_api)
api.add_namespace(extras_api)
api.add_namespace(notifications_api)
api.add_namespace(error_models)
api.add_namespace(error_models)
api.add_namespace(attendees_api)
api.add_namespace(tickets_apt)


@api.documentation
def custom_ui():
    return render_template(
        'swagger/swagger-ui.html',
        title=api.title,
        specs_url=api.specs_url,
        user=current_user)


@api.errorhandler(NotFoundError)
@api.errorhandler(NotAuthorizedError)
@api.errorhandler(PermissionDeniedError)
@api.errorhandler(ValidationError)
@api.errorhandler(InvalidServiceError)
def handle_error(error):
    return error.to_dict(), getattr(error, 'code')


@api.errorhandler
def default_error_handler(error):
    """Returns Internal server error"""
    error = ServerError()
    return error.to_dict(), getattr(error, 'code', 500)

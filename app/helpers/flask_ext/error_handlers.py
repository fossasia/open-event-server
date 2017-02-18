import json

from flask import render_template
from flask import request

from app.api.helpers.errors import NotFoundError, PermissionDeniedError, ServerError, ValidationError

# taken from http://flask.pocoo.org/snippets/45/
def request_wants_json():
    best = request.accept_mimetypes.best_match(
        ['application/json', 'text/html'])
    return best == 'application/json' and request.accept_mimetypes[best] > request.accept_mimetypes['text/html']


def init_error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(e):
        if request_wants_json():
            error = NotFoundError()
            return json.dumps(error.to_dict()), getattr(error, 'code', 404)
        return render_template('gentelella/errors/404.html'), 404

    @app.errorhandler(403)
    def forbidden(e):
        if request_wants_json():
            error = PermissionDeniedError()
            return json.dumps(error.to_dict()), getattr(error, 'code', 403)
        return render_template('gentelella/errors/403.html'), 403

    @app.errorhandler(500)
    def server_error(e):
        if request_wants_json():
            error = ServerError()
            return json.dumps(error.to_dict()), getattr(error, 'code', 500)
        return render_template('gentelella/errors/500.html'), 500

    @app.errorhandler(400)
    def bad_request(e):
        if request_wants_json():
            error = ValidationError(field='unknown')
            return json.dumps(error.to_dict()), getattr(error, 'code', 400)
        return render_template('gentelella/errors/400.html'), 400

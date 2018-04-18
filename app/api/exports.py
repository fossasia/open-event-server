import os

from flask import send_file, make_response, jsonify, url_for, \
    current_app, request, Blueprint
from flask_jwt import jwt_required, current_identity

from app.api.helpers.export_helpers import export_event_json, create_export_job
from app.api.helpers.utilities import TASK_RESULTS
from app.models import db
from app.models.event import Event

export_routes = Blueprint('exports', __name__, url_prefix='/v1')

EXPORT_SETTING = {
    'image': False,
    'video': False,
    'document': False,
    'audio': False
}


@export_routes.route('/events/<string:event_identifier>/export/json', methods=['POST'])
@jwt_required()
def export_event(event_identifier):
    from .helpers.tasks import export_event_task

    settings = EXPORT_SETTING
    settings['image'] = request.json.get('image', False)
    settings['video'] = request.json.get('video', False)
    settings['document'] = request.json.get('document', False)
    settings['audio'] = request.json.get('audio', False)

    if not event_identifier.isdigit():
        event = db.session.query(Event).filter_by(identifier=event_identifier).first()
        event_id = event.id
    else:
        event_id = event_identifier
    # queue task
    task = export_event_task.delay(
        current_identity.email, event_id, settings)
    # create Job
    create_export_job(task.id, event_id)

    # in case of testing
    if current_app.config.get('CELERY_ALWAYS_EAGER'):
        # send_export_mail(event_id, task.get())
        TASK_RESULTS[task.id] = {
            'result': task.get(),
            'state': task.state
        }
    return jsonify(
        task_url=url_for('tasks.celery_task', task_id=task.id)
    )


@export_routes.route('/events/<string:event_id>/exports/<path:path>')
@jwt_required()
def export_download(event_id, path):
    if not path.startswith('/'):
        path = '/' + path
    if not os.path.isfile(path):
        return 'Not Found', 404
    response = make_response(send_file(path))
    response.headers['Content-Disposition'] = 'attachment; filename=event%d.zip' % event_id
    return response


def event_export_task_base(event_id, settings):
    path = export_event_json(event_id, settings)
    if path.startswith('/'):
        path = path[1:]
    return path

from flask import Blueprint, abort, current_app, jsonify, url_for
from flask_jwt_extended import current_user, jwt_required

from app.api.helpers.files import make_frontend_url
from app.api.helpers.import_helpers import (
    create_import_job,
    get_file_from_request,
    import_event_json,
)
from app.api.helpers.utilities import TASK_RESULTS

import_routes = Blueprint('imports', __name__, url_prefix='/v1')


@import_routes.route('/events/import/<string:source_type>', methods=['POST'])
@jwt_required
def import_event(source_type):
    if source_type == 'json':
        file_path = get_file_from_request(['zip'])
    else:
        file_path = None
        abort(404)
    from .helpers.tasks import import_event_task

    task = import_event_task.delay(
        email=current_user.email,
        file=file_path,
        source_type=source_type,
        creator_id=current_user.id,
    )
    # create import job
    create_import_job(task.id)

    # if testing
    if current_app.config.get('CELERY_ALWAYS_EAGER'):
        TASK_RESULTS[task.id] = {'result': task.get(), 'state': task.state}
    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))


def import_event_task_base(task_handle, file_path, source_type='json', creator_id=None):
    new_event = None
    if source_type == 'json':
        new_event = import_event_json(task_handle, file_path, creator_id)
    if new_event:
        url = make_frontend_url(path=f'/events/{new_event.identifier}')
        return {'url': url, 'id': new_event.id, 'event_name': new_event.name}
    return None

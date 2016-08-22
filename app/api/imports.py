from flask.ext.restplus import Resource, Namespace, marshal
from flask import jsonify, url_for, current_app

from app.helpers.data import record_activity
from helpers.import_helpers import get_file_from_request, import_event_json, create_import_job
from helpers.helpers import requires_auth
from helpers.utils import TASK_RESULTS
from events import EVENT


api = Namespace('imports', description='Imports', path='/')


@api.route('/events/import/json')
@api.hide
class EventImportJson(Resource):
    @requires_auth
    def post(self):
        file = get_file_from_request(['zip'])
        from helpers.tasks import import_event_task
        task = import_event_task.delay(file)
        # store import job in db
        try:
            create_import_job(task.id)
        except Exception:
            pass
        # if testing
        if current_app.config.get('CELERY_ALWAYS_EAGER'):
            TASK_RESULTS[task.id] = {
                'result': task.get(),
                'state': task.state
            }
        return jsonify(
            task_url=url_for('api.extras_celery_task', task_id=task.id)
        )


def import_event_task_base(task_handle, file):
    new_event = import_event_json(task_handle, file)
    record_activity('import_event', event_id=new_event.id)
    return marshal(new_event, EVENT)

from flask.ext.restplus import Resource, Namespace, marshal
from flask import jsonify, url_for

from open_event.helpers.data import record_activity
from helpers.import_helpers import get_file_from_request, import_event_json
from helpers.helpers import requires_auth
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
        # http://stackoverflow.com/questions/26379026/resolving-
        # task = celery.current_app.send_task('import.event', [file])
        return jsonify(
            task_id=task.id,
            task_url=url_for('api.extras_celery_task', task_id=task.id)
        )


def import_event_task_base(file):
    new_event = import_event_json(file)
    record_activity('import_event', event_id=new_event.id)
    return marshal(new_event, EVENT)

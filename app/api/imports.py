from flask import g
from flask import jsonify, url_for, current_app
from flask.ext.restplus import Resource, Namespace, marshal
from flask.ext.restplus import abort

from app.helpers.data import record_activity
from app.helpers.importers.ical import ICalImporter
from app.helpers.importers.pentabarfxml import PentabarfImporter
from events import EVENT
from helpers.helpers import requires_auth
from helpers.import_helpers import get_file_from_request, import_event_json, create_import_job, \
    send_import_mail
from helpers.utils import TASK_RESULTS

api = Namespace('imports', description='Imports', path='/')


@api.route('/events/import/<string:source_type>')
@api.hide
class EventImportJson(Resource):
    @requires_auth
    def post(self, source_type):
        if source_type == 'json':
            file_path = get_file_from_request(['zip'])
        elif source_type == 'pentabarf':
            file_path = get_file_from_request(['xml'])
        elif source_type == 'ical':
            file_path = get_file_from_request(['ical', 'ics'])
        else:
            file_path = None
            abort(404)
        from helpers.tasks import import_event_task
        task = import_event_task.delay(file=file_path, source_type=source_type, creator_id=g.user.id)
        # store import job in db
        try:
            create_import_job(task.id)
        except Exception:
            pass
        # if testing
        if current_app.config.get('CELERY_ALWAYS_EAGER'):
            send_import_mail(task.id, task.get())
            TASK_RESULTS[task.id] = {
                'result': task.get(),
                'state': task.state
            }
        return jsonify(
            task_url=url_for('api.extras_celery_task', task_id=task.id)
        )


def import_event_task_base(task_handle, file_path, source_type='json', creator_id=None):
    new_event = None
    if source_type == 'json':
        new_event = import_event_json(task_handle, file_path)
    elif source_type == 'pentabarf':
        new_event = PentabarfImporter.import_data(file_path=file_path, task_handle=task_handle, creator_id=creator_id)
    elif source_type == 'ical':
        new_event = ICalImporter.import_data(file_path=file_path, task_handle=task_handle, creator_id=creator_id)
    if new_event:
        record_activity('import_event', event_id=new_event.id)
        return marshal(new_event, EVENT)
    else:
        return None

import os
from flask import send_file, make_response, jsonify, url_for, current_app
from flask.ext.restplus import Resource, Namespace

from app.helpers.data import record_activity
from helpers.export_helpers import export_event_json
from helpers.utils import TASK_RESULTS
from helpers import custom_fields as fields
from helpers.helpers import nocache, can_access, requires_auth


api = Namespace('exports', description='Exports', path='/')

EXPORT_SETTING = api.model('ExportSetting', {
    'image': fields.Boolean(default=False),
    'video': fields.Boolean(default=False),
    'document': fields.Boolean(default=False),
    'audio': fields.Boolean(default=False)
})


@requires_auth
@can_access
@nocache
@api.route('/events/<int:event_id>/export/json')
@api.hide
class EventExportJson(Resource):
    @api.expect(EXPORT_SETTING)
    def post(self, event_id):
        print self.api.payload
        from helpers.tasks import export_event_task
        task = export_event_task.delay(event_id)
        if current_app.config.get('CELERY_ALWAYS_EAGER'):
            TASK_RESULTS[task.id] = {
                'result': task.get(),
                'state': task.state
            }
        return jsonify(
            task_url=url_for('api.extras_celery_task', task_id=task.id)
        )


@nocache
@api.hide
@api.route('/events/<int:event_id>/exports/<path:path>')
class ExportDownload(Resource):
    def get(self, event_id, path):
        if not path.startswith('/'):
            path = '/' + path
        if not os.path.isfile(path):
            return 'Not Found', 404
        response = make_response(send_file(path))
        response.headers['Content-Disposition'] = 'attachment; filename=event%d.zip' % event_id
        record_activity('export_event', event_id=event_id)
        return response


def event_export_task_base(event_id):
    path = export_event_json(event_id)
    if path.startswith('/'):
        path = path[1:]
    return path

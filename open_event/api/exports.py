from flask import send_file, make_response
from flask.ext.restplus import Resource, Namespace

from helpers.export_helpers import export_event_json
from helpers.helpers import nocache


api = Namespace('event_exports', description='Event Exports', path='/')


@nocache
@api.route('/events/<int:event_id>/export/json')
@api.hide
class EventExportJson(Resource):
    def get(self, event_id):
        path = export_event_json(event_id)
        response = make_response(send_file(path))
        response.headers['Content-Disposition'] = 'attachment; filename=event%d.zip' % event_id
        return response

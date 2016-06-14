from flask.ext.restplus import Resource, Namespace, marshal

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
        new_event = import_event_json(file)
        return marshal(new_event, EVENT)

from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.microlocation import Microlocation as MicrolocationModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('microlocations', description='microlocations', path='/')

_microlocation = api.model('microlocation', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'latitude': fields.Float,
    'longitude': fields.Float,
    'floor': fields.Integer,
    'room': fields.String,
})


@api.route('/events/<int:event_id>/microlocations/<int:microlocation_id>')
@api.response(404, 'Microlocation not found')
@api.response(400, 'Object does not belong to event')
class Microlocation(Resource):
    @api.doc('get_microlocation')
    @api.marshal_with(_microlocation)
    def get(self, event_id, microlocation_id):
        """Fetch a microlocation given its id"""
        return get_object_in_event(MicrolocationModel, microlocation_id,
                                   event_id)


@api.route('/events/<int:event_id>/microlocations')
@api.param('event_id')
class MicrolocationList(Resource):
    @api.doc('list_microlocations')
    @api.marshal_list_with(_microlocation)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(MicrolocationModel, event_id=event_id)

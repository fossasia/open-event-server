from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Format as FormatModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('formats', description='formats', path='/')

_format = api.model('Format', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'label_en': fields.String,
})


@api.route('/events/<int:event_id>/formats/<int:format_id>')
@api.response(404, 'Format not found')
@api.response(400, 'Object does not belong to event')
class Format(Resource):
    @api.doc('get_format')
    @api.marshal_with(_format)
    def get(self, event_id, format_id):
        """Fetch a format given its id"""
        return get_object_in_event(FormatModel, format_id, event_id)


@api.route('/events/<int:event_id>/formats')
@api.param('event_id')
class FormatList(Resource):
    @api.doc('list_formats')
    @api.marshal_list_with(_format)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(FormatModel, event_id=event_id)

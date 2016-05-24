from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.sponsor import Sponsor as SponsorModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('sponsors', description='sponsors', path='/')

_sponsor = api.model('sponsor', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'url': fields.String,
    'logo': fields.String,
})


@api.route('/events/<int:event_id>/sponsors/<int:sponsor_id>')
@api.response(404, 'Sponsor not found')
@api.response(400, 'Object does not belong to event')
class Sponsor(Resource):
    @api.doc('get_sponsor')
    @api.marshal_with(_sponsor)
    def get(self, event_id, sponsor_id):
        """Fetch a sponsor given its id"""
        return get_object_in_event(SponsorModel, sponsor_id, event_id)


@api.route('/events/<int:event_id>/sponsors')
@api.param('event_id')
class SponsorList(Resource):
    @api.doc('list_sponsors')
    @api.marshal_list_with(_sponsor)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(SponsorModel, event_id=event_id)

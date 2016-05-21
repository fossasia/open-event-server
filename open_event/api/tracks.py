from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.track import Track as TrackModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404

api = Namespace('tracks', description='Tracks', path='/')

track = api.model('Track', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'description': fields.String,
    'track_image_url': fields.String,
    # sessions
})


@api.route('/events/<int:event_id>/tracks/<int:id>')
@api.param('id')
@api.response(404, 'Track not found')
class Track(Resource):
    @api.doc('get_track')
    @api.marshal_with(track)
    def get(self, event_id, id):
        """Fetch a track given its id"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_or_404(TrackModel, id)


@api.route('/events/<int:event_id>/tracks')
@api.param('event_id')
class TrackList(Resource):
    @api.doc('list_tracks')
    @api.marshal_list_with(track)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(TrackModel, event_id=event_id)

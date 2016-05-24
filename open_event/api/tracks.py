from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.track import Track as TrackModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('tracks', description='Tracks', path='/')

TRACK_SESSION = api.model('TrackSession', {
    'id': fields.Integer(required=True),
    'title': fields.String,
})

TRACK = api.model('Track', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'description': fields.String,
    'track_image_url': fields.String,
    'sessions': fields.List(fields.Nested(TRACK_SESSION)),
})


@api.route('/events/<int:event_id>/tracks/<int:track_id>')
@api.response(404, 'Track not found')
@api.response(400, 'Object does not belong to event')
class Track(Resource):
    @api.doc('get_track')
    @api.marshal_with(TRACK)
    def get(self, event_id, track_id):
        """Fetch a track given its id"""
        return get_object_in_event(TrackModel, track_id, event_id)


@api.route('/events/<int:event_id>/tracks')
class TrackList(Resource):
    @api.doc('list_tracks')
    @api.marshal_list_with(TRACK)
    def get(self, event_id):
        """List all sessions"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(TrackModel, event_id=event_id)

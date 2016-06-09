from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.track import Track as TrackModel
from custom_fields import ImageUriField, ColorField
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES

api = Namespace('tracks', description='Tracks', path='/')

TRACK_SESSION = api.model('TrackSession', {
    'id': fields.Integer(required=True),
    'title': fields.String,
})

TRACK = api.model('Track', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'description': fields.String,
    'color': ColorField(),
    'track_image_url': ImageUriField(),
    'sessions': fields.List(fields.Nested(TRACK_SESSION)),
})

TRACK_PAGINATED = api.clone('TrackPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(TRACK))
})

TRACK_POST = api.clone('TrackPost', TRACK)
del TRACK_POST['id']
del TRACK_POST['sessions']


# Create DAO
class TrackDAO(ServiceDAO):
    pass

DAO = TrackDAO(model=TrackModel)


@api.route('/events/<int:event_id>/tracks/<int:track_id>')
@api.response(404, 'Track not found')
@api.response(400, 'Track does not belong to event')
class Track(Resource):
    @api.doc('get_track')
    @api.marshal_with(TRACK)
    def get(self, event_id, track_id):
        """Fetch a track given its id"""
        return DAO.get(event_id, track_id)

    @requires_auth
    @api.doc('delete_track')
    @api.marshal_with(TRACK)
    def delete(self, event_id, track_id):
        """Delete a track given its id"""
        return DAO.delete(event_id, track_id)

    @requires_auth
    @api.doc('update_track', responses=PUT_RESPONSES)
    @api.marshal_with(TRACK)
    @api.expect(TRACK_POST, validate=True)
    def put(self, event_id, track_id):
        """Update a track given its id"""
        return DAO.update(event_id, track_id, self.api.payload)


@api.route('/events/<int:event_id>/tracks')
class TrackList(Resource):
    @api.doc('list_tracks')
    @api.marshal_list_with(TRACK)
    def get(self, event_id):
        """List all tracks"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_track', responses=POST_RESPONSES)
    @api.marshal_with(TRACK)
    @api.expect(TRACK_POST, validate=True)
    def post(self, event_id):
        """Create a track"""
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/tracks/page')
class TrackListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_tracks_paginated', params=PAGE_PARAMS)
    @api.marshal_with(TRACK_PAGINATED)
    def get(self, event_id):
        """List tracks in a paginated manner"""
        return get_paginated_list(
            TrackModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

from flask.ext.restplus import Resource, Namespace

from open_event.models.track import Track as TrackModel

from .helpers.helpers import requires_auth
from .helpers.helpers import (
    can_create,
    can_read,
    can_update,
    can_delete
)
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, SERVICE_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('tracks', description='Tracks', path='/')

TRACK_SESSION = api.model('TrackSession', {
    'id': fields.Integer(required=True),
    'title': fields.String(),
})

TRACK = api.model('Track', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'description': fields.String(),
    'color': fields.Color(required=True),
    'track_image_url': fields.Upload(),
    'location': fields.String(),
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

DAO = TrackDAO(TrackModel, TRACK_POST)


@api.route('/events/<int:event_id>/tracks/<int:track_id>')
@api.doc(responses=SERVICE_RESPONSES)
class Track(Resource):
    @requires_auth
    @can_create(DAO)
    @api.doc('get_track')
    @api.marshal_with(TRACK)
    def get(self, event_id, track_id):
        """Fetch a track given its id"""
        return DAO.get(event_id, track_id)

    @requires_auth
    @can_delete(DAO)
    @api.doc('delete_track')
    @api.marshal_with(TRACK)
    def delete(self, event_id, track_id):
        """Delete a track given its id"""
        return DAO.delete(event_id, track_id)

    @requires_auth
    @can_update(DAO)
    @api.doc('update_track', responses=PUT_RESPONSES)
    @api.marshal_with(TRACK)
    @api.expect(TRACK_POST)
    def put(self, event_id, track_id):
        """Update a track given its id"""
        return DAO.update(event_id, track_id, self.api.payload)


@api.route('/events/<int:event_id>/tracks')
class TrackList(Resource):
    @requires_auth
    @can_read(DAO)
    @api.doc('list_tracks')
    @api.marshal_list_with(TRACK)
    def get(self, event_id):
        """List all tracks"""
        return DAO.list(event_id)

    @requires_auth
    @can_create(DAO)
    @api.doc('create_track', responses=POST_RESPONSES)
    @api.marshal_with(TRACK)
    @api.expect(TRACK_POST)
    def post(self, event_id):
        """Create a track"""
        return DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )


@api.route('/events/<int:event_id>/tracks/page')
class TrackListPaginated(Resource, PaginatedResourceBase):
    @requires_auth
    @can_read(DAO)
    @api.doc('list_tracks_paginated', params=PAGE_PARAMS)
    @api.marshal_with(TRACK_PAGINATED)
    def get(self, event_id):
        """List tracks in a paginated manner"""
        args = self.parser.parse_args()
        return DAO.paginated_list(args=args, event_id=event_id)

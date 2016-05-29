from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.speaker import Speaker as SpeakerModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO

api = Namespace('speakers', description='Speakers', path='/')

SPEAKER_SESSION = api.model('SpeakerSession', {
    'id': fields.Integer,
    'title': fields.String,
})

SPEAKER = api.model('Speaker', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'photo': fields.String,
    'biography': fields.String,
    'email': fields.String,
    'web': fields.String,
    'twitter': fields.String,
    'facebook': fields.String,
    'github': fields.String,
    'linkedin': fields.String,
    'organisation': fields.String,
    'position': fields.String,
    'country': fields.String,
    'sessions': fields.List(fields.Nested(SPEAKER_SESSION)),
})

SPEAKER_PAGINATED = api.clone('SpeakerPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPEAKER))
})

SPEAKER_POST = api.clone('SpeakerPost', SPEAKER)
del SPEAKER_POST['id']
del SPEAKER_POST['sessions']  # don't allow adding sessions


# Create DAO
class SpeakerDAO(ServiceDAO):
    pass

DAO = SpeakerDAO(model=SpeakerModel)


@api.route('/events/<int:event_id>/speakers/<int:speaker_id>')
@api.response(404, 'Speaker not found')
@api.response(400, 'Object does not belong to event')
class Speaker(Resource):
    @api.doc('get_speaker')
    @api.marshal_with(SPEAKER)
    def get(self, event_id, speaker_id):
        """Fetch a speaker given its id"""
        return DAO.get(event_id, speaker_id)


@api.route('/events/<int:event_id>/speakers')
@api.param('event_id')
class SpeakerList(Resource):
    @api.doc('list_speakers')
    @api.marshal_list_with(SPEAKER)
    def get(self, event_id):
        """List all speakers"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_speaker')
    @api.marshal_with(SPEAKER)
    @api.expect(SPEAKER_POST, validate=True)
    def post(self, event_id):
        """Create a speaker"""
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/speakers/page')
class SpeakerListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_speakers_paginated')
    @api.param('start')
    @api.param('limit')
    @api.marshal_with(SPEAKER_PAGINATED)
    def get(self, event_id):
        """List speakers in a paginated manner"""
        return get_paginated_list(
            SpeakerModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

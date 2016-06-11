from flask.ext.restplus import Resource, Namespace

from open_event.models.speaker import Speaker as SpeakerModel
import custom_fields as fields
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES

api = Namespace('speakers', description='Speakers', path='/')

SPEAKER_SESSION = api.model('SpeakerSession', {
    'id': fields.Integer(),
    'title': fields.String(),
})

SPEAKER = api.model('Speaker', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'photo': fields.ImageUri(),
    'biography': fields.String(),
    'email': fields.Email(),
    'web': fields.Uri(),
    'twitter': fields.String(),  # not sure for now whether uri or string field
    'facebook': fields.String(),
    'github': fields.String(),
    'linkedin': fields.String(),
    'organisation': fields.String(),
    'position': fields.String(),
    'country': fields.String(),
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
@api.response(400, 'Speaker does not belong to event')
class Speaker(Resource):
    @api.doc('get_speaker')
    @api.marshal_with(SPEAKER)
    def get(self, event_id, speaker_id):
        """Fetch a speaker given its id"""
        return DAO.get(event_id, speaker_id)

    @requires_auth
    @api.doc('delete_speaker')
    @api.marshal_with(SPEAKER)
    def delete(self, event_id, speaker_id):
        """Delete a speaker given its id"""
        return DAO.delete(event_id, speaker_id)

    @requires_auth
    @api.doc('update_speaker', responses=PUT_RESPONSES)
    @api.marshal_with(SPEAKER)
    @api.expect(SPEAKER_POST)
    def put(self, event_id, speaker_id):
        """Update a speaker given its id"""
        DAO.validate(self.api.payload, SPEAKER_POST)
        return DAO.update(event_id, speaker_id, self.api.payload)


@api.route('/events/<int:event_id>/speakers')
class SpeakerList(Resource):
    @api.doc('list_speakers')
    @api.marshal_list_with(SPEAKER)
    def get(self, event_id):
        """List all speakers"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_speaker', responses=POST_RESPONSES)
    @api.marshal_with(SPEAKER)
    @api.expect(SPEAKER_POST)
    def post(self, event_id):
        """Create a speaker"""
        DAO.validate(self.api.payload, SPEAKER_POST)
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/speakers/page')
class SpeakerListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_speakers_paginated', params=PAGE_PARAMS)
    @api.marshal_with(SPEAKER_PAGINATED)
    def get(self, event_id):
        """List speakers in a paginated manner"""
        return get_paginated_list(
            SpeakerModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

from flask.ext.restplus import Resource, Namespace

from open_event.models.speaker import Speaker as SpeakerModel
from open_event.helpers.data_getter import DataGetter

from .helpers.helpers import get_paginated_list, requires_auth, \
    model_custom_form
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO,\
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, SERVICE_RESPONSES
from .helpers import custom_fields as fields
from .helpers.error_docs import customform_error_model


api = Namespace('speakers', description='Speakers', path='/')

SPEAKER_SESSION = api.model('SpeakerSession', {
    'id': fields.Integer(),
    'title': fields.String(),
})

SPEAKER = api.model('Speaker', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'photo': fields.ImageUri(),
    'short_biography': fields.String(),
    'long_biography': fields.String(),
    'email': fields.Email(),
    'mobile': fields.String(),
    'website': fields.Uri(),
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
    def create(self, event_id, data, url):
        data = self.validate(data, event_id)
        return ServiceDAO.create(self, event_id, data, url, validate=False)

    def update(self, event_id, service_id, data):
        data = self.validate(data, event_id)
        return ServiceDAO.update(self, event_id, service_id, data, validate=False)

    def validate(self, data, event_id, model=None):
        form = DataGetter.get_custom_form_elements(event_id)
        if form:
            model = model_custom_form(form.speaker_form, self.post_api_model)
        return ServiceDAO.validate(self, data, model)

DAO = SpeakerDAO(SpeakerModel, SPEAKER_POST)


@api.route('/events/<int:event_id>/speakers/<int:speaker_id>')
@api.doc(responses=SERVICE_RESPONSES)
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
    @api.response(400, 'Custom form error', customform_error_model)
    @api.doc('update_speaker', responses=PUT_RESPONSES)
    @api.marshal_with(SPEAKER)
    @api.expect(SPEAKER_POST)
    def put(self, event_id, speaker_id):
        """Update a speaker given its id"""
        return DAO.update(event_id, speaker_id, self.api.payload)


@api.route('/events/<int:event_id>/speakers')
class SpeakerList(Resource):
    @api.doc('list_speakers')
    @api.marshal_list_with(SPEAKER)
    def get(self, event_id):
        """List all speakers"""
        return DAO.list(event_id)

    @requires_auth
    @api.response(400, 'Custom form error', customform_error_model)
    @api.doc('create_speaker', responses=POST_RESPONSES)
    @api.marshal_with(SPEAKER)
    @api.expect(SPEAKER_POST)
    def post(self, event_id):
        """Create a speaker"""
        return DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )

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

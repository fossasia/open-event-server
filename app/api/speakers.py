from functools import wraps

from flask import g
from flask.ext.restplus import Namespace, marshal_with
from flask_login import current_user

from app.helpers.data_getter import DataGetter
from app.models.speaker import Speaker as SpeakerModel
from .helpers import custom_fields as fields
from .helpers.helpers import (
    can_create,
    can_update,
    can_delete
)
from .helpers.helpers import model_custom_form, requires_auth
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES, SERVICE_RESPONSES
from .helpers.utils import Resource, ETAG_HEADER_DEFN

api = Namespace('speakers', description='Speakers', path='/')

SPEAKER_SESSION = api.model('SpeakerSession', {
    'id': fields.Integer(),
    'title': fields.String(),
})

SPEAKER = api.model('Speaker', {
    'id': fields.Integer(required=True),
    'name': fields.String(required=True),
    'photo': fields.Upload(),
    'short_biography': fields.String(),
    'long_biography': fields.String(),
    'email': fields.Email(required=True),
    'mobile': fields.String(),
    'featured': fields.Boolean(),
    'website': fields.Uri(),
    'twitter': fields.String(),  # not sure for now whether uri or string field
    'facebook': fields.String(),
    'github': fields.String(),
    'linkedin': fields.String(),
    'organisation': fields.String(required=True),
    'position': fields.String(),
    'country': fields.String(required=True),
    'sessions': fields.List(fields.Nested(SPEAKER_SESSION)),
    'city': fields.String(),
    'heard_from': fields.String(),
    'speaking_experience': fields.String(),
    'sponsorship_required': fields.String()
})

SPEAKER_PAGINATED = api.clone('SpeakerPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPEAKER))
})

SPEAKER_POST = api.clone('SpeakerPost', SPEAKER)
del SPEAKER_POST['id']
del SPEAKER_POST['sessions']  # don't allow adding sessions

SPEAKER_PRIVATE = api.clone('SpeakerPrivate', SPEAKER)
del SPEAKER_PRIVATE['email']
del SPEAKER_PRIVATE['mobile']

SPEAKER_PAGINATED_PRIVATE = api.clone('SpeakerPaginatedPrivate', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPEAKER_PRIVATE))
})


# Create DAO
class SpeakerDAO(ServiceDAO):
    version_key = 'speakers_ver'

    def create(self, event_id, data, url):
        data = self.validate(data, event_id)
        return ServiceDAO.create(self, event_id, data, url, validate=False)

    def update(self, event_id, service_id, data):
        data = self.validate(data, event_id, False)
        return ServiceDAO.update(self, event_id, service_id, data, validate=False)

    def validate(self, data, event_id, check_required=True):
        form = DataGetter.get_custom_form_elements(event_id)
        model = None
        if form:
            model = model_custom_form(form.speaker_form, self.post_api_model)
        return ServiceDAO.validate(
            self, data, model, check_required=check_required)


DAO = SpeakerDAO(SpeakerModel, SPEAKER_POST)


# ############
# Response Marshaller
# ############

def speakers_marshal_with(fields=None, fields_private=None):
    """
    Response marshalling for speakers. Doesn't update apidoc
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user = getattr(g, 'user', None)
            event_id = kwargs.get('event_id')
            if user is None and current_user.is_authenticated:
                # in case of GET requests. No requires_auth there
                user = current_user
            if user and (user.has_role(event_id) or user.is_staff):
                model = fields if fields else SPEAKER
            else:
                model = fields_private if fields_private else SPEAKER_PRIVATE
            func2 = marshal_with(model)(func)
            return func2(*args, **kwargs)

        return wrapper

    return decorator


# ############
# API Resource
# ############

@api.route('/events/<int:event_id>/speakers/<int:speaker_id>')
@api.doc(responses=SERVICE_RESPONSES)
class Speaker(Resource):
    @api.doc('get_speaker', model=SPEAKER)
    @api.header(*ETAG_HEADER_DEFN)
    @speakers_marshal_with()
    def get(self, event_id, speaker_id):
        """Fetch a speaker given its id"""
        return DAO.get(event_id, speaker_id)

    @requires_auth
    @can_delete(DAO)
    @api.doc('delete_speaker', model=SPEAKER)
    @speakers_marshal_with()
    def delete(self, event_id, speaker_id):
        """Delete a speaker given its id"""
        return DAO.delete(event_id, speaker_id)

    @requires_auth
    @can_update(DAO)
    @api.doc('update_speaker', responses=PUT_RESPONSES, model=SPEAKER)
    @speakers_marshal_with()
    @api.expect(SPEAKER_POST)
    def put(self, event_id, speaker_id):
        """Update a speaker given its id"""
        return DAO.update(event_id, speaker_id, self.api.payload)


@api.route('/events/<int:event_id>/speakers')
class SpeakerList(Resource):
    @api.doc('list_speakers', model=[SPEAKER])
    @api.header(*ETAG_HEADER_DEFN)
    @speakers_marshal_with()
    def get(self, event_id):
        """List all speakers"""
        return DAO.list(event_id)

    @requires_auth
    @can_create(DAO)
    @api.doc('create_speaker', responses=POST_RESPONSES, model=SPEAKER)
    @speakers_marshal_with()
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
    @api.doc(model=SPEAKER_PAGINATED)
    @api.header(*ETAG_HEADER_DEFN)
    @speakers_marshal_with(fields=SPEAKER_PAGINATED, fields_private=SPEAKER_PAGINATED_PRIVATE)
    def get(self, event_id):
        """List speakers in a paginated manner"""
        args = self.parser.parse_args()
        return DAO.paginated_list(args=args, event_id=event_id)

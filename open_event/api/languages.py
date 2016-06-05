from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Language as LanguageModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES

api = Namespace('languages', description='languages', path='/')

LANGUAGE = api.model('Language', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'label_en': fields.String,
    'label_de': fields.String,
})

LANGUAGE_PAGINATED = api.clone('LanguagePaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(LANGUAGE))
})

LANGUAGE_POST = api.clone('LanguagePost', LANGUAGE)
del LANGUAGE_POST['id']


# Create DAO
class LanguageDAO(ServiceDAO):
    pass

DAO = LanguageDAO(model=LanguageModel)


@api.route('/events/<int:event_id>/languages/<int:language_id>')
@api.response(404, 'Language not found')
@api.response(400, 'Language does not belong to event')
class Language(Resource):
    @api.doc('get_language')
    @api.marshal_with(LANGUAGE)
    def get(self, event_id, language_id):
        """Fetch a language given its id"""
        return DAO.get(event_id, language_id)


@api.route('/events/<int:event_id>/languages')
class LanguageList(Resource):
    @api.doc('list_languages')
    @api.marshal_list_with(LANGUAGE)
    def get(self, event_id):
        """List all languages"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_language', responses=POST_RESPONSES)
    @api.marshal_with(LANGUAGE)
    @api.expect(LANGUAGE_POST, validate=True)
    def post(self, event_id):
        """Create a language"""
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/languages/page')
class LanguageListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_languages_paginated', params=PAGE_PARAMS)
    @api.marshal_with(LANGUAGE_PAGINATED)
    def get(self, event_id):
        """List languages in a paginated manner"""
        return get_paginated_list(
            LanguageModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

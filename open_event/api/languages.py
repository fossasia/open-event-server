from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Language as LanguageModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event,\
    get_paginated_list
from utils import PAGINATED_MODEL, PaginatedResourceBase, PAGE_PARAMS

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


@api.route('/events/<int:event_id>/languages/<int:language_id>')
@api.response(404, 'Language not found')
@api.response(400, 'Language does not belong to event')
class Language(Resource):
    @api.doc('get_language')
    @api.marshal_with(LANGUAGE)
    def get(self, event_id, language_id):
        """Fetch a language given its id"""
        return get_object_in_event(LanguageModel, language_id, event_id)


@api.route('/events/<int:event_id>/languages')
class LanguageList(Resource):
    @api.doc('list_languages')
    @api.marshal_list_with(LANGUAGE)
    def get(self, event_id):
        """List all languages"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(LanguageModel, event_id=event_id)


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

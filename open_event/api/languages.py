from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Language as LanguageModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event

api = Namespace('languages', description='languages', path='/')

LANGUAGE = api.model('Language', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'label_en': fields.String,
    'label_de': fields.String,
})


@api.route('/events/<int:event_id>/languages/<int:language_id>')
@api.response(404, 'Language not found')
@api.response(400, 'Object does not belong to event')
class Language(Resource):
    @api.doc('get_language')
    @api.marshal_with(LANGUAGE)
    def get(self, event_id, language_id):
        """Fetch a language given its id"""
        return get_object_in_event(LanguageModel, language_id, event_id)


@api.route('/events/<int:event_id>/languages')
@api.param('event_id')
class LanguageList(Resource):
    @api.doc('list_languages')
    @api.marshal_list_with(LANGUAGE)
    def get(self, event_id):
        """List all languages"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(LanguageModel, event_id=event_id)

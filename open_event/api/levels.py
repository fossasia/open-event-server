from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Level as LevelModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event,\
    get_paginated_list
from utils import PAGINATED_MODEL, PaginatedResourceBase, PAGE_PARAMS

api = Namespace('levels', description='levels', path='/')

LEVEL = api.model('Level', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'label_en': fields.String,
})

LEVEL_PAGINATED = api.clone('LevelPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(LEVEL))
})


@api.route('/events/<int:event_id>/levels/<int:level_id>')
@api.response(404, 'Level not found')
@api.response(400, 'Level does not belong to event')
class Level(Resource):
    @api.doc('get_level')
    @api.marshal_with(LEVEL)
    def get(self, event_id, level_id):
        """Fetch a level given its id"""
        return get_object_in_event(LevelModel, level_id, event_id)


@api.route('/events/<int:event_id>/levels')
class LevelList(Resource):
    @api.doc('list_levels')
    @api.marshal_list_with(LEVEL)
    def get(self, event_id):
        """List all levels"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(LevelModel, event_id=event_id)


@api.route('/events/<int:event_id>/levels/page')
class LevelListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_levels_paginated', params=PAGE_PARAMS)
    @api.marshal_with(LEVEL_PAGINATED)
    def get(self, event_id):
        """List levels in a paginated manner"""
        return get_paginated_list(
            LevelModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.session import Level as LevelModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, PAGE_PARAMS

api = Namespace('levels', description='levels', path='/')

LEVEL = api.model('Level', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'label_en': fields.String,
})

LEVEL_PAGINATED = api.clone('LevelPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(LEVEL))
})

LEVEL_POST = api.clone('LevelPost', LEVEL)
del LEVEL_POST['id']


# Create DAO
class LevelDAO(ServiceDAO):
    pass

DAO = LevelDAO(model=LevelModel)


@api.route('/events/<int:event_id>/levels/<int:level_id>')
@api.response(404, 'Level not found')
@api.response(400, 'Level does not belong to event')
class Level(Resource):
    @api.doc('get_level')
    @api.marshal_with(LEVEL)
    def get(self, event_id, level_id):
        """Fetch a level given its id"""
        return DAO.get(event_id, level_id)


@api.route('/events/<int:event_id>/levels')
class LevelList(Resource):
    @api.doc('list_levels')
    @api.marshal_list_with(LEVEL)
    def get(self, event_id):
        """List all levels"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_level')
    @api.marshal_with(LEVEL)
    @api.expect(LEVEL_POST, validate=True)
    def post(self, event_id):
        """Create a level"""
        return DAO.create(event_id, self.api.payload, LEVEL_POST)


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

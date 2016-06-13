from flask.ext.restplus import Resource, Namespace
import custom_fields as fields
from open_event.models.microlocation import Microlocation as MicrolocationModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES

api = Namespace('microlocations', description='Microlocations', path='/')

MICROLOCATION = api.model('Microlocation', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'latitude': fields.Float(),
    'longitude': fields.Float(),
    'floor': fields.Integer(),
    'room': fields.String(),
})

MICROLOCATION_PAGINATED = api.clone('MicrolocationPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(MICROLOCATION))
})

MICROLOCATION_POST = api.clone('MicrolocationPost', MICROLOCATION)
del MICROLOCATION_POST['id']


# Create DAO
class MicrolocationDAO(ServiceDAO):
    pass

DAO = MicrolocationDAO(MicrolocationModel, MICROLOCATION_POST)


@api.route('/events/<int:event_id>/microlocations/<int:microlocation_id>')
@api.response(404, 'Microlocation not found')
@api.response(400, 'Microlocation does not belong to event')
class Microlocation(Resource):
    @api.doc('get_microlocation')
    @api.marshal_with(MICROLOCATION)
    def get(self, event_id, microlocation_id):
        """Fetch a microlocation given its id"""
        return DAO.get(event_id, microlocation_id)

    @requires_auth
    @api.doc('delete_microlocation')
    @api.marshal_with(MICROLOCATION)
    def delete(self, event_id, microlocation_id):
        """Delete a microlocation given its id"""
        return DAO.delete(event_id, microlocation_id)

    @requires_auth
    @api.doc('update_microlocation', responses=PUT_RESPONSES)
    @api.marshal_with(MICROLOCATION)
    @api.expect(MICROLOCATION_POST)
    def put(self, event_id, microlocation_id):
        """Update a microlocation given its id"""
        return DAO.update(event_id, microlocation_id, self.api.payload)


@api.route('/events/<int:event_id>/microlocations')
class MicrolocationList(Resource):
    @api.doc('list_microlocations')
    @api.marshal_list_with(MICROLOCATION)
    def get(self, event_id):
        """List all microlocations"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_microlocation', responses=POST_RESPONSES)
    @api.marshal_with(MICROLOCATION)
    @api.expect(MICROLOCATION_POST)
    def post(self, event_id):
        """Create a microlocation"""
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/microlocations/page')
class MicrolocationListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_microlocations_paginated', params=PAGE_PARAMS)
    @api.marshal_with(MICROLOCATION_PAGINATED)
    def get(self, event_id):
        """List microlocations in a paginated manner"""
        return get_paginated_list(
            MicrolocationModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

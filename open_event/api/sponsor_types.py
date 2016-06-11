from flask.ext.restplus import Resource, Namespace
import custom_fields as fields
from open_event.models.sponsor import SponsorType as SponsorTypeModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES

api = Namespace('sponsor_types', description='SponsorTypes', path='/')

SPONSOR_TYPE = api.model('SponsorType', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
})

SPONSOR_TYPE_PAGINATED = api.clone('SponsorTypePaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPONSOR_TYPE))
})

SPONSOR_TYPE_POST = api.clone('SponsorTypePost', SPONSOR_TYPE)
del SPONSOR_TYPE_POST['id']


# Create DAO
class SponsorTypeDAO(ServiceDAO):
    pass

DAO = SponsorTypeDAO(model=SponsorTypeModel)


@api.route('/events/<int:event_id>/sponsor_types/<int:sponsor_type_id>')
@api.response(404, 'Sponsor Type not found')
@api.response(400, 'Sponsor Type does not belong to event')
class SponsorType(Resource):
    @api.doc('get_sponsor_type')
    @api.marshal_with(SPONSOR_TYPE)
    def get(self, event_id, sponsor_type_id):
        """Fetch a sponsor_type given its id"""
        return DAO.get(event_id, sponsor_type_id)

    @requires_auth
    @api.doc('delete_sponsor_type')
    @api.marshal_with(SPONSOR_TYPE)
    def delete(self, event_id, sponsor_type_id):
        """Delete a sponsor_type given its id"""
        return DAO.delete(event_id, sponsor_type_id)

    @requires_auth
    @api.doc('update_sponsor_type', responses=PUT_RESPONSES)
    @api.marshal_with(SPONSOR_TYPE)
    @api.expect(SPONSOR_TYPE_POST)
    def put(self, event_id, sponsor_type_id):
        """Update a sponsor_type given its id"""
        DAO.validate(self.api.payload, SPONSOR_TYPE_POST)
        return DAO.update(event_id, sponsor_type_id, self.api.payload)


@api.route('/events/<int:event_id>/sponsor_types')
class SponsorTypeList(Resource):
    @api.doc('list_sponsor_types')
    @api.marshal_list_with(SPONSOR_TYPE)
    def get(self, event_id):
        """List all sponsor_types"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_sponsor_type', responses=POST_RESPONSES)
    @api.marshal_with(SPONSOR_TYPE)
    @api.expect(SPONSOR_TYPE_POST)
    def post(self, event_id):
        """Create a sponsor_type"""
        DAO.validate(self.api.payload, SPONSOR_TYPE_POST)
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/sponsor_types/page')
class SponsorTypeListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_sponsor_types_paginated', params=PAGE_PARAMS)
    @api.marshal_with(SPONSOR_TYPE_PAGINATED)
    def get(self, event_id):
        """List sponsor_types in a paginated manner"""
        return get_paginated_list(
            SponsorTypeModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

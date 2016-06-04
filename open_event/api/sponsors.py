from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.sponsor import Sponsor as SponsorModel
from .helpers import get_paginated_list, requires_auth
from utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO

api = Namespace('sponsors', description='sponsors', path='/')

SPONSOR = api.model('Sponsor', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'url': fields.String,
    'logo': fields.String,
})

SPONSOR_PAGINATED = api.clone('SponsorPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPONSOR))
})

SPONSOR_POST = api.clone('SponsorPost', SPONSOR)
del SPONSOR_POST['id']


# Create DAO
class SponsorDAO(ServiceDAO):
    pass

DAO = SponsorDAO(model=SponsorModel)


@api.route('/events/<int:event_id>/sponsors/<int:sponsor_id>')
@api.response(404, 'Sponsor not found')
@api.response(400, 'Object does not belong to event')
class Sponsor(Resource):
    @api.doc('get_sponsor')
    @api.marshal_with(SPONSOR)
    def get(self, event_id, sponsor_id):
        """Fetch a sponsor given its id"""
        return DAO.get(event_id, sponsor_id)


@api.route('/events/<int:event_id>/sponsors')
@api.param('event_id')
class SponsorList(Resource):
    @api.doc('list_sponsors')
    @api.marshal_list_with(SPONSOR)
    def get(self, event_id):
        """List all sponsors"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_sponsor')
    @api.marshal_with(SPONSOR)
    @api.expect(SPONSOR_POST, validate=True)
    def post(self, event_id):
        """Create a sponsor"""
        return DAO.create(event_id, self.api.payload)


@api.route('/events/<int:event_id>/sponsors/page')
class SponsorListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_sponsors_paginated')
    @api.param('start')
    @api.param('limit')
    @api.marshal_with(SPONSOR_PAGINATED)
    def get(self, event_id):
        """List sponsors in a paginated manner"""
        return get_paginated_list(
            SponsorModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

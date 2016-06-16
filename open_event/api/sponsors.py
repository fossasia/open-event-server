from flask.ext.restplus import Resource, Namespace

from open_event.models.sponsor import Sponsor as SponsorModel

from .helpers.helpers import get_paginated_list, requires_auth, get_object_in_event
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('sponsors', description='Sponsors', path='/')

SPONSOR = api.model('Sponsor', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'url': fields.Uri(),
    'logo': fields.ImageUri(),
    'description': fields.String(),
    'level': fields.String(),
    'sponsor_type': fields.String(),
})

SPONSOR_PAGINATED = api.clone('SponsorPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPONSOR))
})

SPONSOR_POST = api.clone('SponsorPost', SPONSOR)
del SPONSOR_POST['id']


# Create DAO
class SponsorDAO(ServiceDAO):
    def list_types(self, event_id):
        sponsors = self.list(event_id)
        return list(set(
            sponsor.sponsor_type for sponsor in sponsors
            if sponsor.sponsor_type))


DAO = SponsorDAO(SponsorModel, SPONSOR_POST)


@api.route('/events/<int:event_id>/sponsors/<int:sponsor_id>')
@api.response(404, 'Sponsor not found')
@api.response(400, 'Sponsor does not belong to event')
class Sponsor(Resource):
    @api.doc('get_sponsor')
    @api.marshal_with(SPONSOR)
    def get(self, event_id, sponsor_id):
        """Fetch a sponsor given its id"""
        return DAO.get(event_id, sponsor_id)

    @requires_auth
    @api.doc('delete_sponsor')
    @api.marshal_with(SPONSOR)
    def delete(self, event_id, sponsor_id):
        """Delete a sponsor given its id"""
        return DAO.delete(event_id, sponsor_id)

    @requires_auth
    @api.doc('update_sponsor', responses=PUT_RESPONSES)
    @api.marshal_with(SPONSOR)
    @api.expect(SPONSOR_POST)
    def put(self, event_id, sponsor_id):
        """Update a sponsor given its id"""
        return DAO.update(event_id, sponsor_id, self.api.payload)


@api.route('/events/<int:event_id>/sponsors')
class SponsorList(Resource):
    @api.doc('list_sponsors')
    @api.marshal_list_with(SPONSOR)
    def get(self, event_id):
        """List all sponsors"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_sponsor', responses=POST_RESPONSES)
    @api.marshal_with(SPONSOR)
    @api.expect(SPONSOR_POST)
    def post(self, event_id):
        """Create a sponsor"""
        return DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )


@api.route('/events/<int:event_id>/sponsors/types')
class SponsorTypesList(Resource):
    @api.doc('list_sponsor_types', model=[fields.String()])
    def get(self, event_id):
        """List all sponsor types"""
        return DAO.list_types(event_id)


@api.route('/events/<int:event_id>/sponsors/page')
class SponsorListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_sponsors_paginated', params=PAGE_PARAMS)
    @api.marshal_with(SPONSOR_PAGINATED)
    def get(self, event_id):
        """List sponsors in a paginated manner"""
        return get_paginated_list(
            SponsorModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

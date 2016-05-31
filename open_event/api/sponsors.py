from flask.ext.restplus import Resource, Namespace, fields

from open_event.models.sponsor import Sponsor as SponsorModel
from open_event.models.event import Event as EventModel
from .helpers import get_object_list, get_object_or_404, get_object_in_event,\
    get_paginated_list
from utils import PAGINATED_MODEL, PaginatedResourceBase
from custom_fields import UriField, ImageUriField

api = Namespace('sponsors', description='sponsors', path='/')

SPONSOR = api.model('Sponsor', {
    'id': fields.Integer(required=True),
    'name': fields.String,
    'url': UriField(),
    'logo': ImageUriField(),
})

SPONSOR_PAGINATED = api.clone('SponsorPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(SPONSOR))
})


@api.route('/events/<int:event_id>/sponsors/<int:sponsor_id>')
@api.response(404, 'Sponsor not found')
@api.response(400, 'Object does not belong to event')
class Sponsor(Resource):
    @api.doc('get_sponsor')
    @api.marshal_with(SPONSOR)
    def get(self, event_id, sponsor_id):
        """Fetch a sponsor given its id"""
        return get_object_in_event(SponsorModel, sponsor_id, event_id)


@api.route('/events/<int:event_id>/sponsors')
@api.param('event_id')
class SponsorList(Resource):
    @api.doc('list_sponsors')
    @api.marshal_list_with(SPONSOR)
    def get(self, event_id):
        """List all sponsors"""
        # Check if an event with `event_id` exists
        get_object_or_404(EventModel, event_id)

        return get_object_list(SponsorModel, event_id=event_id)


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

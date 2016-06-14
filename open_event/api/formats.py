from flask.ext.restplus import Resource, Namespace

from open_event.models.session import Format as FormatModel

from .helpers.helpers import get_paginated_list, requires_auth
from .helpers.utils import PAGINATED_MODEL, PaginatedResourceBase, ServiceDAO, \
    PAGE_PARAMS, POST_RESPONSES, PUT_RESPONSES
from .helpers import custom_fields as fields

api = Namespace('formats', description='Formats', path='/')

# Create models
FORMAT = api.model('Format', {
    'id': fields.Integer(required=True),
    'name': fields.String(),
    'label_en': fields.String(),
})

FORMAT_PAGINATED = api.clone('FormatPaginated', PAGINATED_MODEL, {
    'results': fields.List(fields.Nested(FORMAT))
})

FORMAT_POST = api.clone('FormatPost', FORMAT)
del FORMAT_POST['id']


# Create DAO
class FormatDAO(ServiceDAO):
    pass

DAO = FormatDAO(FormatModel, FORMAT_POST)


@api.route('/events/<int:event_id>/formats/<int:format_id>')
@api.response(404, 'Format not found')
@api.response(400, 'Format does not belong to event')
class Format(Resource):
    @api.doc('get_format')
    @api.marshal_with(FORMAT)
    def get(self, event_id, format_id):
        """Fetch a format given its id"""
        return DAO.get(event_id, format_id)

    @requires_auth
    @api.doc('delete_format')
    @api.marshal_with(FORMAT)
    def delete(self, event_id, format_id):
        """Delete a format given its id"""
        return DAO.delete(event_id, format_id)

    @requires_auth
    @api.doc('update_format', responses=PUT_RESPONSES)
    @api.marshal_with(FORMAT)
    @api.expect(FORMAT_POST)
    def put(self, event_id, format_id):
        """Update a format given its id"""
        return DAO.update(event_id, format_id, self.api.payload)


@api.route('/events/<int:event_id>/formats')
class FormatList(Resource):
    @api.doc('list_formats')
    @api.marshal_list_with(FORMAT)
    def get(self, event_id):
        """List all formats"""
        return DAO.list(event_id)

    @requires_auth
    @api.doc('create_format', responses=POST_RESPONSES)
    @api.marshal_with(FORMAT)
    @api.expect(FORMAT_POST)
    def post(self, event_id):
        """Create a format"""
        return DAO.create(
            event_id,
            self.api.payload,
            self.api.url_for(self, event_id=event_id)
        )

@api.route('/events/<int:event_id>/formats/page')
class FormatListPaginated(Resource, PaginatedResourceBase):
    @api.doc('list_formats_paginated', params=PAGE_PARAMS)
    @api.marshal_with(FORMAT_PAGINATED)
    def get(self, event_id):
        """List formats in a paginated manner"""
        return get_paginated_list(
            FormatModel,
            self.api.url_for(self, event_id=event_id),
            args=self.parser.parse_args(),
            event_id=event_id
        )

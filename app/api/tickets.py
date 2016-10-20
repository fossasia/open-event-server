from flask.ext.restplus import Namespace

from app.helpers.ticketing import TicketingManager

from .helpers.helpers import (
    requires_auth,
    can_access)
from .helpers.utils import POST_RESPONSES
from .helpers.utils import Resource
from .helpers import custom_fields as fields
from ..helpers.data_getter import DataGetter

api = Namespace('tickets', description='Tickets', path='/')

ORDER = api.model('Order', {
    'id': fields.Integer(),
    'identifier': fields.String(),
    'amount': fields.Float(),
    'paid_via': fields.String(),
    'invoice_number': fields.String(),
    'payment_mode': fields.String(),
    'status': fields.String(),
    'completed_at': fields.DateTime(),
})

TICKET = api.model('Ticket', {
    'id': fields.Integer(),
    'name': fields.String(),
    'description': fields.String(),
    'type': fields.String(),
    'price': fields.Float(),
    'quantity': fields.Integer(),
})


@api.route('/events/<int:event_id>/tickets/')
class TicketsList(Resource):
    @requires_auth
    @api.doc('tickets', responses=POST_RESPONSES)
    @api.marshal_list_with(TICKET)
    def get(self, event_id):
        """Get tickets of the event"""
        return DataGetter.get_sales_open_tickets(event_id=event_id).all()


@api.route('/events/<int:event_id>/tickets/<int:ticket_id>')
class Ticket(Resource):
    @requires_auth
    @api.doc('ticket', responses=POST_RESPONSES)
    @api.marshal_with(TICKET)
    def get(self, event_id, ticket_id):
        """Get information about a ticket"""
        return TicketingManager.get_ticket(ticket_id=ticket_id)

@api.route('/events/<int:event_id>/orders/<string:identifier>')
class Order(Resource):
    @requires_auth
    @api.doc('order', responses=POST_RESPONSES)
    @api.marshal_with(ORDER)
    def get(self, event_id, identifier):
        """Get information about a ticket"""
        return TicketingManager.get_order_by_identifier(identifier=identifier)



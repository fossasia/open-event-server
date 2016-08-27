from flask.ext.restplus import Namespace

from app.helpers.ticketing import TicketingManager

from .helpers.helpers import (
    requires_auth,
    can_access)
from .helpers.utils import POST_RESPONSES
from .helpers.utils import Resource
from .helpers import custom_fields as fields

api = Namespace('ticketing', description='Ticketing', path='/')

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

TICKET_HOLDER = api.model('TicketHolder', {
    'id': fields.Integer(),
    'firstname': fields.String(),
    'lastname': fields.String(),
    'email': fields.Email(),
    'checked_in': fields.Boolean(),
    'order': fields.Nested(ORDER, allow_null=False),
    'ticket': fields.Nested(TICKET, allow_null=False)
})

@api.route('/events/<int:event_id>/attendees/')
class AttendeesList(Resource):
    @requires_auth
    @can_access
    @api.doc('check_in_toggle', responses=POST_RESPONSES)
    @api.marshal_list_with(TICKET_HOLDER)
    def get(self, event_id):
        """Get attendees of the event"""
        return TicketingManager.get_attendees(event_id)

@api.route('/events/<int:event_id>/attendees/check_in_toggle/<holder_identifier>')
class AttendeeCheckInToggle(Resource):
    @requires_auth
    @can_access
    @api.doc('check_in_toggle', responses=POST_RESPONSES)
    @api.marshal_with(TICKET_HOLDER)
    def post(self, event_id, holder_identifier):
        """Toggle and Attendee's Checked in State"""
        holder = TicketingManager.attendee_check_in_out(holder_identifier)
        return holder, 200

@api.route('/events/<int:event_id>/attendees/check_in_toggle/<holder_identifier>/check_in')
class AttendeeCheckIn(Resource):
    @requires_auth
    @can_access
    @api.doc('check_in_toggle', responses=POST_RESPONSES)
    @api.marshal_with(TICKET_HOLDER)
    def post(self, event_id, holder_identifier):
        """Check in attendee"""
        holder = TicketingManager.attendee_check_in_out(holder_identifier, True)
        return holder, 200

@api.route('/events/<int:event_id>/attendees/check_in_toggle/<holder_identifier>/check_out')
class AttendeeCheckOut(Resource):
    @requires_auth
    @can_access
    @api.doc('check_in_toggle', responses=POST_RESPONSES)
    @api.marshal_with(TICKET_HOLDER)
    def post(self, event_id, holder_identifier):
        """Check out attendee"""
        holder = TicketingManager.attendee_check_in_out(holder_identifier, False)
        return holder, 200

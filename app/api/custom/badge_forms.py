from flask import Blueprint, request
from flask.helpers import send_from_directory
from flask_jwt_extended import jwt_required

from app.api.helpers.badge_forms import create_preivew_badge_pdf, create_print_badge_pdf
from app.api.helpers.errors import ForbiddenError, NotFoundError
from app.api.helpers.permission_manager import has_access
from app.models.badge_form import BadgeForms
from app.models.ticket_holder import TicketHolder

badge_forms_routes = Blueprint(
    'badge_forms_routes', __name__, url_prefix='/v1/badge-forms'
)


@badge_forms_routes.route('/preivew-badge-pdf', methods=['POST'])
@jwt_required
def preivew_badge_pdf():
    """Preview Badge Template PDF"""

    badgeForms = request.json.get('badgeForms')
    if badgeForms is None:
        raise NotFoundError(
            {'source': ''}, 'This badge form is not associated with any ticket'
        )

    file_path = create_preivew_badge_pdf(badgeForms)
    return send_from_directory('../', file_path, as_attachment=True)


@badge_forms_routes.route('/print-badge-pdf', methods=['POST'])
@jwt_required
def print_badge_pdf():
    """Print Badge PDF with information Attendee"""

    attendee_id = request.json.get('attendee_id')
    list_field_show = request.json.get('list_field_show')
    ticketHolders = TicketHolder.query.filter_by(id=attendee_id).first()
    if ticketHolders is None:
        raise NotFoundError(
            {'source': ''}, 'This ticket holder is not associated with any ticket'
        )
    badgeForms = BadgeForms.query.filter_by(
        badge_id=ticketHolders.ticket.badge_id
    ).first()
    if badgeForms is None:
        raise NotFoundError(
            {'source': ''}, 'This badge form is not associated with any ticket'
        )
    if not has_access('is_coorganizer', event_id=badgeForms.event_id):
        raise ForbiddenError({'source': ''}, 'Unauthorized Access')

    file_path = create_print_badge_pdf(badgeForms, ticketHolders, list_field_show)
    return send_from_directory('../', file_path, as_attachment=True)

from flask import Blueprint, jsonify, request
from flask.helpers import send_from_directory, url_for
from flask_jwt_extended import jwt_required

from app.api.helpers.badge_forms import create_preivew_badge_pdf
from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.export_helpers import (
    comma_separated_params_to_list,
    create_export_badge_job,
)
from app.api.helpers.permission_manager import has_access
from app.models.badge_form import BadgeForms
from app.models.ticket_holder import TicketHolder

badge_forms_routes = Blueprint(
    'badge_forms_routes', __name__, url_prefix='/v1/badge-forms'
)


@badge_forms_routes.route('/preview-badge-pdf', methods=['POST'])
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


@badge_forms_routes.route('/print-badge-pdf', methods=['GET'])
@jwt_required
def print_badge_pdf():
    """Print Badge Template PDF"""
    from ..helpers.tasks import create_print_badge_pdf

    if not request.args.get('attendee_id', False):
        raise NotFoundError(
            {'parameter': 'attendee_id'}, "attendee_id is missing from your request."
        )
    if not request.args.get('list_field_show', False):
        raise NotFoundError(
            {'parameter': 'list_field_show'},
            "list_field_show is missing from your request.",
        )
    attendee_id = request.args.get('attendee_id')
    list_field_show = comma_separated_params_to_list(request.args.get('list_field_show'))
    if isinstance(attendee_id, int) or (
        isinstance(attendee_id, str) and attendee_id.isdigit()
    ):
        ticket_holder = TicketHolder.query.filter_by(id=attendee_id).first()
    else:
        raise UnprocessableEntityError(
            {'pointer': 'ticket_holder'}, "Invalid Attendee Id"
        )
    if ticket_holder is None:
        raise NotFoundError(
            {'source': ''}, 'This ticket holder is not associated with any ticket'
        )
    badge_form = BadgeForms.query.filter_by(
        badge_id=ticket_holder.ticket.badge_id
    ).first()
    if badge_form is None:
        raise NotFoundError(
            {'source': ''}, 'This badge form is not associated with any ticket'
        )
    if not has_access('is_coorganizer', event_id=ticket_holder.event_id):
        raise ForbiddenError({'source': ''}, 'Unauthorized Access')

    task = create_print_badge_pdf.delay(attendee_id, list_field_show)
    create_export_badge_job(task.id, ticket_holder.event_id, attendee_id)

    return jsonify(task_url=url_for('tasks.celery_task', task_id=task.id))

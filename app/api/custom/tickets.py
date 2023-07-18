from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required

from app.api.helpers.errors import NotFoundError
from app.models.badge_field_form import BadgeFieldForms
from app.models.ticket import Ticket

ticket_routes = Blueprint('ticket_routes', __name__, url_prefix='/v1/tickets')


@ticket_routes.route('/<int:ticket_id>/badge-forms', methods=['GET'])
@jwt_required
def get_badge_field(ticket_id):
    """Get Badge Field"""
    ticket = Ticket.query.filter_by(id=ticket_id).first()
    if ticket is None:
        raise NotFoundError(
            {'source': ''}, 'This ticket holder is not associated with any ticket'
        )

    badgeFieldForms = BadgeFieldForms.query.filter_by(badge_id=ticket.badge_id).all()
    if badgeFieldForms is None:
        raise NotFoundError(
            {'source': ''}, 'This badge field form is not associated with any ticket'
        )

    result = []
    for badgeFieldForm in badgeFieldForms:
        result.append(badgeFieldForm.get_badge_field())

    return jsonify(result)

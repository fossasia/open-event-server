from flask import Blueprint, abort, jsonify, make_response, request
from flask_jwt_extended import current_user
from flask_rest_jsonapi.exceptions import ObjectNotFound
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import safe_query_by_id
from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.order import Order
from app.models.ticket_holder import TicketHolder

attendee_blueprint = Blueprint('attendee_blueprint', __name__, url_prefix='/v1')


# TODO(Areeb): Deprecate and remove
@attendee_blueprint.route('/attendees/send-receipt', methods=['POST'])
@jwt_required
def send_receipt():
    """
    Send receipts to attendees related to the provided order.
    :return:
    """
    order_identifier = request.json.get('order-identifier')
    if order_identifier:
        try:
            order = db.session.query(Order).filter_by(identifier=order_identifier).one()
        except NoResultFound:
            raise NotFoundError({'parameter': '{order_identifier}'}, "Order not found")

        if (order.user_id != current_user.id) and (
            not has_access('is_registrar', event_id=order.event_id)
        ):
            raise ForbiddenError(
                {'source': ''},
                'You need to be the event organizer or order buyer to send receipts.',
            )
        if order.status != 'completed':
            abort(
                make_response(
                    jsonify(error="Cannot send receipt for an incomplete order"), 409
                )
            )
        else:
            send_email_to_attendees(order)
            return jsonify(message="receipt sent to attendees")
    else:
        raise UnprocessableEntityError({'source': ''}, 'Order identifier missing')


@attendee_blueprint.route('/states', methods=['GET'])
@jwt_required
def check_attendee_state():
    """
    API to check attendee state is check in/registered
    @return: user is registered or not
    """
    from app.models.event import Event

    if not request.args.get('event_id', False):
        raise NotFoundError(
            {'parameter': 'event_id'}, "event_id is missing from your request."
        )
    if not request.args.get('attendee_id', False):
        raise NotFoundError(
            {'parameter': 'attendee_id'}, "attendee_id is missing from your request."
        )
    event_id = request.args.get('event_id')
    attendee_id = request.args.get('attendee_id')
    if event_id is not None:
        validate_param_as_id(event_id)
    if attendee_id is not None:
        validate_param_as_id(attendee_id)
    try:
        event = safe_query_by_id(Event, event_id)
    except ObjectNotFound:
        raise NotFoundError({'parameter': f'{event_id}'}, "Event not found.")
    try:
        attendee = safe_query_by_id(TicketHolder, attendee_id)
    except ObjectNotFound:
        raise NotFoundError({'parameter': f'{attendee_id}'}, "Attendee not found.")
    if event.id != attendee.event_id:
        raise UnprocessableEntityError(
            {'parameter': 'Attendee'},
            "Attendee not belong to this event.",
        )
    return jsonify(
        {
            'is_registered': attendee.is_registered,
            'register_times': attendee.register_times,
        }
    )


def validate_param_as_id(param):
    """
    validate id if integer or not
    @param param: param to check
    """
    if not (isinstance(param, int) or (isinstance(param, str) and param.isdigit())):
        raise UnprocessableEntityError(
            {'parameter': f'{param}'}, f'{param} is not a valid id'
        )

from flask import Blueprint, abort, jsonify, make_response, request
from flask_jwt_extended import current_user
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.permission_manager import has_access
from app.api.helpers.permissions import jwt_required
from app.models import db
from app.models.order import Order

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

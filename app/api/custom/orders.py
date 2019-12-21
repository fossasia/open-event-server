from flask import Blueprint, jsonify, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound


from app.models import db
from app.api.auth import return_file
from app.api.helpers.db import safe_query
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError, NotFoundError
from app.api.helpers.order import calculate_order_amount, create_pdf_tickets_for_holder
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.storage import generate_hash
from app.api.helpers.ticketing import TicketingManager
from app.api.helpers.permission_manager import has_access
from app.extensions.limiter import limiter
from app.models.discount_code import DiscountCode
from app.models.order import Order

order_blueprint = Blueprint('order_blueprint', __name__, url_prefix='/v1/orders')
ticket_blueprint = Blueprint('ticket_blueprint', __name__, url_prefix='/v1/tickets')


@ticket_blueprint.route('/<string:order_identifier>')
@order_blueprint.route('/<string:order_identifier>/tickets-pdf')
@jwt_required
def ticket_attendee_authorized(order_identifier):
    if current_user:
        try:
            order = Order.query.filter_by(identifier=order_identifier).first()
        except NoResultFound:
            return NotFoundError({'source': ''}, 'This ticket is not associated with any order').respond()
        if current_user.can_download_tickets(order):
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            file_path = '../generated/tickets/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            try:
                return return_file('ticket', file_path, order_identifier)
            except FileNotFoundError:
                create_pdf_tickets_for_holder(order)
                return return_file('ticket', file_path, order_identifier)
        else:
            return ForbiddenError({'source': ''}, 'Unauthorized Access').respond()
    else:
        return ForbiddenError({'source': ''}, 'Authentication Required to access ticket').respond()


@order_blueprint.route('/resend-email', methods=['POST'])
@limiter.limit(
    '5/minute', key_func=lambda: request.json['data']['user'], error_message='Limit for this action exceeded'
)
@limiter.limit(
    '60/minute', error_message='Limit for this action exceeded'
)
def resend_emails():
    """
    Sends confirmation email for pending and completed orders on organizer request
    :param order_identifier:
    :return: JSON response if the email was succesfully sent
    """
    order_identifier = request.json['data']['order']
    order = safe_query(db, Order, 'identifier', order_identifier, 'identifier')
    if (has_access('is_coorganizer', event_id=order.event_id)):
        if order.status == 'completed' or order.status == 'placed':
            # fetch tickets attachment
            order_identifier = order.identifier
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            ticket_path = 'generated/tickets/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'
            key = UPLOAD_PATHS['pdf']['order'].format(identifier=order_identifier)
            invoice_path = 'generated/invoices/{}/{}/'.format(key, generate_hash(key)) + order_identifier + '.pdf'

            # send email.
            send_email_to_attendees(order=order, purchaser_id=current_user.id, attachments=[ticket_path, invoice_path])
            return jsonify(status=True, message="Verification emails for order : {} has been sent succesfully".
                           format(order_identifier))
        else:
            return UnprocessableEntityError({'source': 'data/order'},
                                            "Only placed and completed orders have confirmation").respond()
    else:
        return ForbiddenError({'source': ''}, "Co-Organizer Access Required").respond()


@order_blueprint.route('/calculate-amount', methods=['POST'])
@jwt_required
def calculate_amount():
    data = request.get_json()
    tickets = data['tickets']
    discount_code = None
    if 'discount-code' in data:
        discount_code_id = data['discount-code']
        discount_code = safe_query(db, DiscountCode, 'id', discount_code_id, 'id')
        if not TicketingManager.match_discount_quantity(discount_code, tickets, None):
            return UnprocessableEntityError({'source': 'discount-code'}, 'Discount Usage Exceeded').respond()

    return jsonify(calculate_order_amount(tickets, discount_code))

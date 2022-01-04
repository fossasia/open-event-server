import os

from datetime import datetime


from flask import Blueprint, jsonify, make_response, request
from flask.helpers import send_from_directory
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app.api.custom.schema.order_amount import OrderAmountInputSchema
from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.order import calculate_order_amount, create_pdf_tickets_for_holder, on_order_completed
from app.api.helpers.permission_manager import has_access
from app.api.orders import validate_attendees
from app.api.schema.orders import OrderSchema
from app.extensions.limiter import limiter
from app.models import db
from app.models.order import Order
from app.models.order import OrderTicket
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder
from app.api.helpers.payment import StripePaymentsManager


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
            raise NotFoundError(
                {'source': ''}, 'This ticket is not associated with any order'
            )
        if (
            has_access(
                'is_coorganizer_or_user_itself',
                event_id=order.event_id,
                user_id=order.user_id,
            )
            or order.is_attendee(current_user)
        ):
            file_path = order.ticket_pdf_path
            if not os.path.isfile(file_path):
                create_pdf_tickets_for_holder(order)
            return send_from_directory('../', file_path, as_attachment=True)
        else:
            raise ForbiddenError({'source': ''}, 'Unauthorized Access')
    else:
        raise ForbiddenError({'source': ''}, 'Authentication Required to access ticket')


@order_blueprint.route('/resend-email', methods=['POST'])
@limiter.limit(
    '5/minute',
    key_func=lambda: request.json['data']['user'],
    error_message='Limit for this action exceeded',
)
@limiter.limit('60/minute', error_message='Limit for this action exceeded')
def resend_emails():
    """
    Sends confirmation email for pending and completed orders on organizer request
    :param order_identifier:
    :return: JSON response if the email was successfully sent
    """
    order_identifier = request.json['data']['order']
    order = safe_query(Order, 'identifier', order_identifier, 'identifier')
    if has_access('is_coorganizer', event_id=order.event_id):
        if order.status == 'completed' or order.status == 'placed':
            send_email_to_attendees(order)
            return jsonify(
                status=True,
                message="Verification emails for order : {} has been sent successfully".format(
                    order_identifier
                ),
            )
        raise UnprocessableEntityError(
            {'source': 'data/order'},
            "Only placed and completed orders have confirmation",
        )
    raise ForbiddenError({'source': ''}, "Co-Organizer Access Required")


@order_blueprint.route('/calculate-amount', methods=['POST'])
def calculate_amount():
    data, errors = OrderAmountInputSchema().load(request.get_json())
    if errors:
        return make_response(jsonify(errors), 422)
    return jsonify(calculate_order_amount(data['tickets'], data.get('discount_code')))


@order_blueprint.route('/create-order', methods=['POST'])
@jwt_required
def create_order():
    data, errors = OrderAmountInputSchema().load(request.get_json())
    if errors:
        return make_response(jsonify(errors), 422)

    tickets_dict = data['tickets']
    order_amount = calculate_order_amount(tickets_dict, data.get('discount_code'))
    ticket_ids = {ticket['id'] for ticket in tickets_dict}
    ticket_map = {int(ticket['id']): ticket for ticket in tickets_dict}
    tickets = (
        Ticket.query.filter_by(deleted_at=None).filter(Ticket.id.in_(ticket_ids)).all()
    )

    if not tickets:
        raise UnprocessableEntityError(
            {'source': 'tickets'},
            "Tickets missing in Order request",
        )

    event = tickets[0].event

    try:
        attendees = []
        for ticket in tickets:
            for _ in range(ticket_map[ticket.id]['quantity']):
                ticket.raise_if_unavailable()
                attendees.append(
                    TicketHolder(firstname='', lastname='', ticket=ticket, event=event)
                )
                db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e

    validate_attendees({attendee.id for attendee in attendees})

    if data.get('amount') is not None and (
        current_user.is_staff or has_access('is_coorganizer', event_id=event.id)
    ):
        # If organizer or admin has overrided the amount of order
        order_amount['total'] = data['amount']

    order = Order(
        amount=order_amount['total'],
        event=event,
        discount_code_id=data.get('discount_code'),
        ticket_holders=attendees,
    )
    db.session.commit()
    order.populate_and_save()

    order_tickets = OrderTicket.query.filter_by(order_id=order.id).all()
    for order_ticket in order_tickets:
        ticket_info = ticket_map[order_ticket.ticket.id]
        order_ticket.price = ticket_info.get('price')
        save_to_db(order_ticket)
    
    return OrderSchema().dump(order)


@order_blueprint.route('/attendees/<int:attendee_id>.pdf')
@jwt_required
def ticket_attendee_pdf(attendee_id):
    ticket_holder = TicketHolder.query.get(attendee_id)
    if ticket_holder is None:
        raise NotFoundError(
            {'source': ''}, 'This attendee is not associated with any ticket'
        )

    if not (
        current_user.is_staff
        or ticket_holder.order.user_id == current_user.id
        or ticket_holder.user == current_user
        or has_access(
            'is_coorganizer_or_user_itself',
            event_id=ticket_holder.event_id,
            user_id=ticket_holder.user.id,
        )
    ):
        raise ForbiddenError({'source': ''}, 'Unauthorized Access')
    file_path = ticket_holder.pdf_url_path
    if not os.path.isfile(file_path):
        create_pdf_tickets_for_holder(ticket_holder.order)
    return send_from_directory('../', file_path, as_attachment=True)

@order_blueprint.route('/<string:order_identifier>/verify', methods=['POST'])
def verify_order_payment(order_identifier):

    order = Order.query.filter_by(identifier=order_identifier).first()
    
    if order.payment_mode == 'stripe':
        try:
            payment_intent = StripePaymentsManager.retrieve_payment_intent(order.event, order.stripe_payment_intent_id)
        except Exception as e:
            raise e

        if payment_intent['status'] == 'succeeded':
            order.status = 'completed'
            order.completed_at = datetime.utcnow()
            order.paid_via = payment_intent['charges']['data'][0]['payment_method_details']['type']
            order.transaction_id = payment_intent['charges']['data'][0]['balance_transaction']
            if payment_intent['charges']['data'][0]['payment_method_details']['type'] == 'card' :
                order.brand = payment_intent['charges']['data'][0]['payment_method_details']['card']['brand']
                order.exp_month = payment_intent['charges']['data'][0]['payment_method_details']['card']['exp_month']
                order.exp_year = payment_intent['charges']['data'][0]['payment_method_details']['card']['exp_year']
                order.last4 = payment_intent['charges']['data'][0]['payment_method_details']['card']['last4']
            save_to_db(order)

            on_order_completed(order)


    return jsonify({ 'payment_status': order.status})

from datetime import datetime

import pytz
from flask import Blueprint, jsonify, make_response, request
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app.api.auth import return_file
from app.api.custom.schema.order_amount import OrderAmountInputSchema
from app.api.helpers.db import get_count, safe_query
from app.api.helpers.errors import ForbiddenError, NotFoundError, UnprocessableEntityError
from app.api.helpers.files import make_frontend_url
from app.api.helpers.mail import send_email_to_attendees, send_order_cancel_email
from app.api.helpers.notification import (
    send_notif_ticket_cancel,
    send_notif_ticket_purchase_organizer,
    send_notif_to_attendees,
)
from app.api.helpers.order import calculate_order_amount, create_pdf_tickets_for_holder
from app.api.helpers.permission_manager import has_access
from app.api.helpers.storage import UPLOAD_PATHS, generate_hash
from app.api.orders import validate_attendees
from app.api.schema.orders import OrderSchema
from app.extensions.limiter import limiter
from app.models import db
from app.models.custom_form import CustomForms
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder

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
        if current_user.can_download_tickets(order):
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            file_path = (
                '../generated/tickets/{}/{}/'.format(key, generate_hash(key))
                + order_identifier
                + '.pdf'
            )
            try:
                return return_file('ticket', file_path, order_identifier)
            except FileNotFoundError:
                create_pdf_tickets_for_holder(order)
                return return_file('ticket', file_path, order_identifier)
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
            # fetch tickets attachment
            order_identifier = order.identifier
            key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
            ticket_path = (
                'generated/tickets/{}/{}/'.format(key, generate_hash(key))
                + order_identifier
                + '.pdf'
            )
            key = UPLOAD_PATHS['pdf']['order'].format(identifier=order_identifier)
            invoice_path = (
                'generated/invoices/{}/{}/'.format(key, generate_hash(key))
                + order_identifier
                + '.pdf'
            )

            # send email.
            send_email_to_attendees(
                order=order,
                purchaser_id=current_user.id,
                attachments=[ticket_path, invoice_path],
            )
            return jsonify(
                status=True,
                message="Verification emails for order : {} has been sent successfully".format(
                    order_identifier
                ),
            )
        else:
            raise UnprocessableEntityError(
                {'source': 'data/order'},
                "Only placed and completed orders have confirmation",
            )
    else:
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
            {'source': 'tickets'}, "Tickets missing in Order request",
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
    order = Order(
        amount=order_amount['total'],
        event=event,
        discount_code_id=data.get('discount_code'),
        ticket_holders=attendees,
    )
    db.session.commit()
    order.populate_and_save()

    return OrderSchema().dumps(order)


@order_blueprint.route('/complete-order/<order_id>', methods=['PATCH'])
@jwt_required
def complete_order(order_id):
    data = request.get_json()
    for attribute in data:
        data[attribute.replace('-', '_')] = data.pop(attribute)
    order = Order.query.filter_by(id=order_id).first()
    order_schema = OrderSchema()
    if (not has_access('is_coorganizer', event_id=order.event_id)) and (
        not current_user.id == order.user_id
    ):
        return make_response(
            jsonify(status='Access Forbidden', error='You cannot update an order.'), 403
        )
    if has_access('is_coorganizer', event_id=order.event_id) and 'status' in data:
        if data['status'] != 'cancelled':
            return make_response(
                jsonify(status='Access Forbidden', error='You can only cancel an order.'),
                403,
            )
        elif data['status'] == 'cancelled':
            order.status = 'cancelled'
            db.session.add(order)
            attendees = (
                db.session.query(TicketHolder)
                .filter_by(order_id=order_id, deleted_at=None)
                .all()
            )
            for attendee in attendees:
                attendee.deleted_at = datetime.now(pytz.utc)
                db.session.add(attendee)
            db.session.commit()
            send_order_cancel_email(order)
            send_notif_ticket_cancel(order)
            return order_schema.dump(order)
    updated_attendees = data['attendees']
    for updated_attendee in updated_attendees:
        for attribute in updated_attendee:
            updated_attendee[attribute.replace('-', '_')] = updated_attendee.pop(
                attribute
            )
    if get_count(db.session.query(TicketHolder).filter_by(order_id=order_id)) != len(
        updated_attendees
    ):
        return make_response(
            jsonify(
                status='Unprocessable Entity',
                error='You need to provide info of all attendees.',
            ),
            422,
        )
    else:
        attendees = (
            db.session.query(TicketHolder)
            .filter_by(order_id=order_id, deleted_at=None)
            .all()
        )
    form_fields = (
        db.session.query(CustomForms)
        .filter_by(
            event_id=order.event_id, form='attendee', is_included=True, deleted_at=None
        )
        .all()
    )
    for attendee, updated_attendee in zip(attendees, updated_attendees):
        for field in form_fields:
            if (
                field.is_required is True
                and field.field_identifier not in updated_attendee
            ):
                return make_response(
                    jsonify(
                        status='Unprocessable Entity',
                        error='{} is a required field.'.format(field.field_identifier),
                    ),
                    422,
                )
            if field.field_identifier in updated_attendee:
                setattr(
                    attendee,
                    field.field_identifier,
                    updated_attendee[field.field_identifier],
                )
        db.session.add(attendee)
    # modified_at not getting filled
    if order.amount == 0:
        order.status = 'completed'
        order.completed_at = datetime.utcnow()
    elif order.amount > 0:
        if 'payment_mode' not in data:
            return make_response(
                jsonify(
                    status='Unprocessable Entity', error='Payment mode not specified.'
                ),
                422,
            )
        if data['payment_mode'] in ['bank', 'cheque', 'onsite']:
            order.status = 'placed'
            order.completed_at = datetime.utcnow()
        else:
            order.status = 'pending'
        if 'is_billing_enabled' in data:
            if data['is_billing_enabled']:
                if (
                    ('company' not in data)
                    or ('address' not in data)
                    or ('city' not in data)
                    or ('zipcode' not in data)
                    or ('country' not in data)
                ):
                    return make_response(
                        jsonify(
                            status='Unprocessable Entity',
                            error='Billing information incomplete.',
                        ),
                        422,
                    )
            else:
                return make_response(
                    jsonify(
                        status='Unprocessable Entity',
                        error='Billing information incomplete.',
                    ),
                    422,
                )
        else:
            return make_response(
                jsonify(
                    status='Unprocessable Entity',
                    error='Billing information is mandatory ' 'for this order.',
                ),
                422,
            )
        order.company = data['company']
        order.address = data['address']
        order.city = data['city']
        order.zipcode = data['zipcode']
        order.country = data['country']
        order.payment_mode = data['payment_mode']
        if 'state' in data:
            order.state = data['state']
        if 'tax_business_info' in data:
            order.tax_business_info = data['tax_business_info']
    db.session.add(order)
    db.session.commit()
    create_pdf_tickets_for_holder(order)
    if (order.status == 'completed' or order.status == 'placed') and (
        order.deleted_at is None
    ):
        order_identifier = order.identifier

        key = UPLOAD_PATHS['pdf']['tickets_all'].format(identifier=order_identifier)
        ticket_path = (
            'generated/tickets/{}/{}/'.format(key, generate_hash(key))
            + order_identifier
            + '.pdf'
        )

        key = UPLOAD_PATHS['pdf']['order'].format(identifier=order_identifier)
        invoice_path = (
            'generated/invoices/{}/{}/'.format(key, generate_hash(key))
            + order_identifier
            + '.pdf'
        )

        # send email and notifications.
        send_email_to_attendees(
            order=order,
            purchaser_id=current_user.id,
            attachments=[ticket_path, invoice_path],
        )

        send_notif_to_attendees(order, current_user.id)
        order_url = make_frontend_url(
            path='/orders/{identifier}'.format(identifier=order.identifier)
        )
        for organizer in order.event.organizers:
            send_notif_ticket_purchase_organizer(
                organizer,
                order.invoice_number,
                order_url,
                order.event.name,
                order.identifier,
            )
        if order.event.owner:
            send_notif_ticket_purchase_organizer(
                order.event.owner,
                order.invoice_number,
                order_url,
                order.event.name,
                order.identifier,
            )

    return order_schema.dump(order)

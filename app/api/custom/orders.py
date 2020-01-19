from flask import Blueprint, jsonify, request, make_response
from flask_jwt_extended import current_user, jwt_required
from sqlalchemy.orm.exc import NoResultFound

from app.models import db
from app.api.auth import return_file
from app.api.helpers.db import safe_query, get_count
from app.api.helpers.mail import send_email_to_attendees
from app.api.helpers.errors import ForbiddenError, UnprocessableEntityError, NotFoundError
from app.api.helpers.order import calculate_order_amount, create_pdf_tickets_for_holder
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.storage import generate_hash
from app.api.schema.attendees import AttendeeSchema
from app.api.schema.orders import OrderSchema
from app.api.helpers.permission_manager import has_access
from app.extensions.limiter import limiter
from app.models.order import Order, OrderTicket
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
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


def calculate_order_amount_wrapper(data):
    tickets = data['tickets']
    discount_code = None
    if 'discount-code' in data:
        discount_code_id = data['discount-code']
        discount_code = safe_query(db, DiscountCode, 'id', discount_code_id, 'id')
    return tickets, discount_code


@order_blueprint.route('/calculate-amount', methods=['POST'])
@jwt_required
def calculate_amount():
    data = request.get_json()
    tickets, discount_code = calculate_order_amount_wrapper(data)
    return jsonify(calculate_order_amount(tickets, discount_code))


@order_blueprint.route('/create-order', methods=['POST'])
@jwt_required
def create_order():
    data = request.get_json()
    tickets, discount_code = calculate_order_amount_wrapper(data)
    attendee = data['attendee']
    for attribute in attendee:
        attendee[attribute.replace('-', '_')] = attendee.pop(attribute)
    schema = AttendeeSchema()
    json_api_attendee = {"data": {"attributes": data['attendee'], "type": "attendee"}}
    result = schema.load(json_api_attendee)
    if result.errors:
        return make_response(jsonify(result.errors), 422)
    ticket_ids = {int(ticket['id']) for ticket in tickets}
    quantity = {int(ticket['id']): ticket['quantity'] for ticket in tickets}
    ticket_list = db.session.query(Ticket).filter(Ticket.id.in_(ticket_ids)).filter_by(event_id=data['event_id'],
                                                                                       deleted_at=None).all()
    ticket_ids_found = {ticket_information.id for ticket_information in ticket_list}
    tickets_not_found = ticket_ids - ticket_ids_found
    if tickets_not_found:
        return make_response(jsonify(status='Order Unsuccessful', error='Tickets with id {} were not found in Event {}.'
                                     .format(tickets_not_found, data['event_id'])), 404)
    for ticket_info in ticket_list:
        if (ticket_info.quantity - get_count(db.session.query(TicketHolder.id).filter_by(
              ticket_id=int(ticket_info.id), deleted_at=None))) < quantity[ticket_info.id]:
            return make_response(jsonify(status='Order Unsuccessful', error='Ticket already sold out.'), 409)
    attendee_list = []
    for ticket in tickets:
        for ticket_amount in range(ticket['quantity']):
            attendee = TicketHolder(**result[0], event_id=int(data['event_id']), ticket_id=int(ticket['id']))
            db.session.add(attendee)
            attendee_list.append(attendee)
    # created_at not getting filled
    ticket_pricing = calculate_order_amount(tickets, discount_code)
    if not has_access('is_coorganizer', event_id=data['event_id']):
        data['status'] = 'initializing'
    # create on site attendees
    # check if order already exists for this attendee.
    # check for free tickets and verified user
    order = Order(amount=ticket_pricing['total_amount'], user_id=current_user.id, event_id=int(data['event_id']),
                  status=data['status'])
    db.session.add(order)
    db.session.commit()
    db.session.refresh(order)
    order_tickets = {}
    for holder in attendee_list:
        holder.order_id = order.id
        db.session.add(holder)
        if not order_tickets.get(holder.ticket_id):
            order_tickets[holder.ticket_id] = 1
        else:
            order_tickets[holder.ticket_id] += 1

    create_pdf_tickets_for_holder(order)

    for ticket in order_tickets:
        od = OrderTicket(order_id=order.id, ticket_id=ticket, quantity=order_tickets[ticket])
        db.session.add(od)

    order.quantity = order.tickets_count
    db.session.add(order)
    db.session.commit()
    db.session.refresh(order)
    order_schema = OrderSchema()
    return order_schema.dump(order)


@order_blueprint.route('/complete-order/<order_id>', methods=['PATCH'])
@jwt_required
def complete_order(order_id):
    data = request.get_json()
    for attribute in data:
        data[attribute.replace('-', '_')] = data.pop(attribute)
    order = Order.query.filter_by(id=order_id).first()
    order_schema = OrderSchema()
    if (not has_access('is_coorganizer', event_id=order.event_id)) and (not current_user.id == order.user_id):
        return make_response(jsonify(status='Access Forbidden', error='You cannot update an order.'), 403)
    if has_access('is_coorganizer', event_id=order.event_id) and 'status' in data:
        if data['status'] != 'cancelled':
            return make_response(jsonify(status='Access Forbidden', error='You can only cancel an order.'), 403)
        elif data['status'] == 'cancelled':
            order.status = 'cancelled'
            db.session.add(order)
            db.session.commit()
            # delete attendee after cancellation of order
            return order_schema.dump(order)
    updated_attendees = data['attendees']
    for updated_attendee in updated_attendees:
        for attribute in updated_attendee:
            updated_attendee[attribute.replace('-', '_')] = updated_attendee.pop(attribute)
    if get_count(db.session.query(TicketHolder).filter_by(order_id=order_id)) != len(updated_attendees):
        return make_response(jsonify(status='Unprocessable Entity', error='You need to provide info of all attendees.')
                             , 422)
    else:
        attendees = db.session.query(TicketHolder).filter_by(order_id=order_id, deleted_at=None).all()
    form_fields = db.session.query(CustomForms).filter_by(event_id=order.event_id, form='attendee', is_included=True,
                                                          deleted_at=None).all()
    for attendee, updated_attendee in zip(attendees, updated_attendees):
        for field in form_fields:
            if field.is_required is True and field.field_identifier not in updated_attendee:
                return make_response(jsonify(status='Unprocessable Entity', error='{} is a required field.'
                                             .format(field.field_identifier)), 422)
            if field.field_identifier in updated_attendee:
                setattr(attendee, field.field_identifier, updated_attendee[field.field_identifier])
        db.session.add(attendee)
    # modified_at not getting filled
    if order.amount == 0:
        order.status = 'completed'
    elif order.amount > 0:
        if 'payment_mode' not in data:
            return make_response(jsonify(status='Unprocessable Entity', error='Payment mode not specified.'), 422)
        if data['payment_mode'] in ['bank', 'cheque', 'onsite']:
            order.status = 'placed'
        else:
            order.status = 'pending'
        if 'is_billing_enabled' in data:
            if data['is_billing_enabled']:
                if ('company' not in data) or ('address' not in data) or ('city' not in data) \
                      or ('zipcode' not in data) or ('country' not in data):
                    return make_response(jsonify(status='Unprocessable Entity', error='Billing information incomplete.')
                                         , 422)
            else:
                return make_response(jsonify(status='Unprocessable Entity', error='Billing information incomplete.')
                                     , 422)
        else:
            return make_response(jsonify(status='Unprocessable Entity', error='Billing information is mandatory '
                                                                              'for this order.'), 422)
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
    # add ticketing pdf logic
    db.session.add(order)
    db.session.commit()
    return order_schema.dump(order)

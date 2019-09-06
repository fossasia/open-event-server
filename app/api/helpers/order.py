import logging
from datetime import timedelta, datetime, timezone

from flask import render_template

from app.settings import get_settings
from app.api.helpers import ticketing
from app.api.helpers.db import save_to_db, safe_query_without_soft_deleted_entries, get_count
from app.api.helpers.exceptions import UnprocessableEntity, ConflictException
from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db
from app.models.ticket import Ticket
from app.models.ticket_fee import TicketFees
from app.models.ticket_holder import TicketHolder
from app.models.order import OrderTicket


def delete_related_attendees_for_order(order):
    """
    Delete the associated attendees of an order when it is cancelled/deleted/expired
    :param order: Order whose attendees have to be deleted.
    :return:
    """
    for ticket_holder in order.ticket_holders:
        db.session.delete(ticket_holder)
        try:
            db.session.commit()
        except Exception as e:
            logging.error('DB Exception! %s' % e)
            db.session.rollback()


def set_expiry_for_order(order, override=False):
    """
    Expire the order after the time slot(10 minutes) if the order is initializing.
    Also expires the order if we want to expire an order regardless of the state and time.
    :param order: Order to be expired.
    :param override: flag to force expiry.
    :return:
    """
    order_expiry_time = get_settings()['order_expiry_time']
    if order and not order.paid_via and (override or (order.status == 'initializing' and (
                order.created_at +
                timedelta(minutes=order_expiry_time)) < datetime.now(timezone.utc))):
            order.status = 'expired'
            delete_related_attendees_for_order(order)
            save_to_db(order)
    return order


def create_pdf_tickets_for_holder(order):
    """
    Create tickets and invoices for the holders of an order.
    :param order: The order for which to create tickets for.
    """
    if order.status == 'completed' or order.status == 'placed':
        pdf = create_save_pdf(render_template('pdf/ticket_purchaser.html', order=order),
                              UPLOAD_PATHS['pdf']['tickets_all'],
                              dir_path='/static/uploads/pdf/tickets/', identifier=order.identifier, upload_dir='generated/tickets/')

        order.tickets_pdf_url = pdf

        for holder in order.ticket_holders:
            if (not holder.user) or holder.user.id != order.user_id:
                # holder is not the order buyer.
                pdf = create_save_pdf(render_template('pdf/ticket_attendee.html', order=order, holder=holder),
                                      UPLOAD_PATHS['pdf']['tickets_all'],
                                      dir_path='/static/uploads/pdf/tickets/', identifier=order.identifier, upload_dir='generated/tickets/')
            else:
                # holder is the order buyer.
                pdf = order.tickets_pdf_url
            holder.pdf_url = pdf
            save_to_db(holder)

        # create order invoices pdf
        order_tickets = OrderTicket.query.filter_by(order_id=order.id, deleted_at=None).all()

        create_save_pdf(render_template('pdf/order_invoice.html', order=order, event=order.event,
                        tax=order.event.tax, order_tickets=order_tickets),
                        UPLOAD_PATHS['pdf']['order'], dir_path='/static/uploads/pdf/tickets/',
                        identifier=order.identifier, upload_dir='generated/invoices/')
        save_to_db(order)


def create_onsite_attendees_for_order(data):
    """
    Creates on site ticket holders for an order and adds it into the request data.
    :param data: data initially passed in the POST request for order.
    :return:
    """
    on_site_tickets = data.get('on_site_tickets')

    if not on_site_tickets:
        raise UnprocessableEntity({'pointer': 'data/attributes/on_site_tickets'}, 'on_site_tickets info missing')

    data['ticket_holders'] = []

    for on_site_ticket in on_site_tickets:
        ticket_id = on_site_ticket['id']
        quantity = int(on_site_ticket['quantity'])

        ticket = safe_query_without_soft_deleted_entries(db, Ticket, 'id', ticket_id, 'ticket_id')

        ticket_sold_count = get_count(db.session.query(TicketHolder.id).
                                      filter_by(ticket_id=int(ticket.id), deleted_at=None))

        # Check if the ticket is already sold out or not.
        if ticket_sold_count + quantity > ticket.quantity:
            # delete the already created attendees.
            for holder in data['ticket_holders']:
                ticket_holder = db.session.query(TicketHolder).filter(id == int(holder)).one()
                db.session.delete(ticket_holder)
                try:
                    db.session.commit()
                except Exception as e:
                    logging.error('DB Exception! %s' % e)
                    db.session.rollback()

            raise ConflictException(
                {'pointer': '/data/attributes/on_site_tickets'},
                "Ticket with id: {} already sold out. You can buy at most {} tickets".format(ticket_id,
                                                                                             ticket.quantity -
                                                                                             ticket_sold_count)
            )

        for _ in range(1, quantity):
            ticket_holder = TicketHolder(firstname='onsite', lastname='attendee', email='example@example.com',
                                         ticket_id=ticket.id, event_id=data.get('event'))
            save_to_db(ticket_holder)
            data['ticket_holders'].append(ticket_holder.id)

    # delete from the data.
    del data['on_site_tickets']


def calculate_order_amount(tickets, discount_code):
    event = tax = tax_included = fees = None
    total_amount = total_tax = total_discount = 0.0
    ticket_list = []
    for ticket_info in tickets:
        tax_amount = tax_percent = 0.0
        tax_data = {}
        discount_amount = discount_percent = 0.0
        discount_data = {}
        sub_total = ticket_fee = 0.0

        ticket_identifier = ticket_info['id']
        quantity = ticket_info['quantity']
        ticket = safe_query_without_soft_deleted_entries(db, Ticket, 'id', ticket_identifier, 'id')
        if not event:
            event = ticket.event
            fees = TicketFees.query.filter_by(currency=event.payment_currency).first()
        elif ticket.event.id != event.id:
            raise UnprocessableEntity({'source': 'data/tickets'}, "Invalid Ticket")

        if not tax and event.tax:
            tax = event.tax
            tax_included = tax.is_tax_included_in_price

        if ticket.type == 'donation':
            price = ticket_info.get('price')
            if not price or price > ticket.max_price or price < ticket.min_price:
                raise UnprocessableEntity({'source': 'data/tickets'}, "Price for donation ticket invalid")
        else:
            price = ticket.price

        if discount_code:
            for code in ticket.discount_codes:
                if discount_code.id == code.id:
                    if code.type == 'amount':
                        discount_amount = code.value
                        discount_percent = (discount_amount / price) * 100
                    else:
                        discount_amount = (price * code.value)/100
                        discount_percent = code.value
                    discount_data = {
                        'code': discount_code.code,
                        'percent': round(discount_percent, 2),
                        'amount': round(discount_amount, 2)
                    }

        if tax:
            if not tax_included:
                tax_amount = ((price - discount_amount) * tax.rate)/100
                tax_percent = tax.rate
            else:
                tax_amount = ((price - discount_amount) * tax.rate)/(100 + tax.rate)
                tax_percent = tax.rate
            tax_data = {
                'percent': round(tax_percent, 2),
                'amount': round(tax_amount, 2),
            }

        total_tax = total_tax + tax_amount * quantity
        total_discount = total_discount + discount_amount*quantity
        if fees and not ticket.is_fee_absorbed:
            ticket_fee = fees.service_fee * (price * quantity) / 100
            if ticket_fee > fees.maximum_fee:
                ticket_fee = fees.maximum_fee
        if tax_included:
            sub_total = ticket_fee + (price - discount_amount)*quantity
        else:
            sub_total = ticket_fee + (price + tax_amount - discount_amount)*quantity
        total_amount = total_amount + sub_total
        ticket_list.append({
            'id': ticket.id,
            'name': ticket.name,
            'price': price,
            'quantity': quantity,
            'discount': discount_data,
            'tax': tax_data,
            'ticket_fee': round(ticket_fee, 2),
            'sub_total': round(sub_total, 2)
        })
    return dict(tax_included=tax_included, total_amount=round(total_amount, 2), total_tax=round(total_tax, 2),
                total_discount=round(total_discount, 2), tickets=ticket_list)

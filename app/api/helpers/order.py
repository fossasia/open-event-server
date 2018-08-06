import logging
from datetime import timedelta, datetime, timezone

from flask import render_template

from app.api.helpers import ticketing
from app.api.helpers.db import save_to_db, safe_query_without_soft_deleted_entries, get_count
from app.api.helpers.exceptions import UnprocessableEntity, ConflictException
from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder


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
    Expire the order after the time slot(10 minutes) if the order is pending.
    Also expires the order if we want to expire an order regardless of the state and time.
    :param order: Order to be expired.
    :param override: flag to force expiry.
    :return:
    """
    if order and not order.paid_via and (override or (order.status == 'pending' and (
                order.created_at +
                timedelta(minutes=order.event.order_expiry_time)) < datetime.now(timezone.utc))):
            order.status = 'expired'
            delete_related_attendees_for_order(order)
            save_to_db(order)
    return order


def create_pdf_tickets_for_holder(order):
    """
    Create tickets for the holders of an order.
    :param order: The order for which to create tickets for.
    """
    if order.status == 'completed':
        pdf = create_save_pdf(render_template('pdf/ticket_purchaser.html', order=order),
                              UPLOAD_PATHS['pdf']['ticket_attendee'],
                              dir_path='/static/uploads/pdf/tickets/')
        order.tickets_pdf_url = pdf

        for holder in order.ticket_holders:
            if (not holder.user) or holder.user.id != order.user_id:
                # holder is not the order buyer.
                pdf = create_save_pdf(render_template('pdf/ticket_attendee.html', order=order, holder=holder),
                                      UPLOAD_PATHS['pdf']['ticket_attendee'],
                                      dir_path='/static/uploads/pdf/tickets/')
            else:
                # holder is the order buyer.
                pdf = order.tickets_pdf_url
            holder.pdf_url = pdf
            save_to_db(holder)

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

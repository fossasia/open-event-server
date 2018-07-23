import logging
from datetime import timedelta, datetime, timezone

from flask import render_template

from app.api.helpers import ticketing
from app.api.helpers.db import save_to_db
from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db


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
                timedelta(minutes=ticketing.TicketingManager.get_order_expiry())) < datetime.now(timezone.utc))):
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

import logging
from datetime import timedelta, datetime, timezone

from app.api.helpers import ticketing
from app.api.helpers.db import save_to_db
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

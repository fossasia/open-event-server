import logging
from datetime import timedelta, datetime, timezone

from app.api.helpers.db import save_to_db
from app.api.helpers import ticketing


def delete_related_attendees_for_order(self, order):
    """
    Delete the associated attendees of an order when it is cancelled/deleted/expired
    :param self:
    :param order: Order whose attendees have to be deleted.
    :return:
    """
    for ticket_holder in order.ticket_holders:
        self.session.delete(ticket_holder)
        try:
            self.session.commit()
        except Exception as e:
            logging.error('DB Exception! %s' % e)
            self.session.rollback()


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
            save_to_db(order)
    return order

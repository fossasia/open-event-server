import logging


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

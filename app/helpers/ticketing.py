"""Copyright 2016 Niranjan Rajendran"""
import binascii
import os

from datetime import timedelta, datetime
from sqlalchemy import func

from app.helpers.data import save_to_db
from app.helpers.helpers import string_empty
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder
from app.models.order import OrderTicket

def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count

def represents_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


class TicketingManager(object):
    """All ticketing and orders related functions"""

    @staticmethod
    def get_order_expiry():
        return 10

    @staticmethod
    def get_new_order_identifier():
        identifier = binascii.b2a_hex(os.urandom(32))
        count = get_count(Order.query.filter_by(identifier=identifier))
        if count == 0:
            return identifier
        else:
            return TicketingManager.get_new_order_identifier()

    @staticmethod
    def get_ticket(ticket_id):
        return Ticket.query.get(ticket_id)

    @staticmethod
    def get_order(order_id):
        return Ticket.query.get(order_id)

    @staticmethod
    def get_order_by_identifier(identifier):
        return Order.query.filter_by(identifier=identifier).one()

    @staticmethod
    def get_and_set_expiry(identifier, override=False):
        if type(identifier) is Order:
            order = identifier
        elif represents_int(identifier):
            order = TicketingManager.get_order(identifier)
        else:
            order = TicketingManager.get_order_by_identifier(identifier)

        if order:
            if override \
                or (order.state == 'pending' and
                    (order.created_at + timedelta(minutes=TicketingManager.get_order_expiry())) < datetime.now()):
                order.state = 'expired'
                save_to_db(order)
        return order

    @staticmethod
    def create_order(form):
        order = Order()
        order.state = 'pending'
        order.identifier = TicketingManager.get_new_order_identifier()
        order.event_id = form.get('event_id')
        ticket_ids = form.getlist('ticket_ids[]')

        ticket_quantity = form.getlist('ticket_quantities[]')
        amount = 0
        for index, id in enumerate(ticket_ids):
            if not string_empty(id) and int(ticket_quantity[index]) > 0:
                order_ticket = OrderTicket()
                order_ticket.ticket = TicketingManager.get_ticket(id)
                order_ticket.quantity = int(ticket_quantity[index])
                order.tickets.append(order_ticket)
                amount = amount + (order_ticket.ticket.price * order_ticket.quantity)

        order.amount = amount

        save_to_db(order)
        return order



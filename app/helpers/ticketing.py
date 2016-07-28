"""Copyright 2016 Niranjan Rajendran"""
import binascii
import os

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

class TicketingManager(object):
    """All ticketing and orders related functions"""

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
    def get_order_by_identifier(identifier):
        return Order.query.filter_by(identifier=identifier).one()

    @staticmethod
    def create_order(form):
        order = Order()
        order.identifier = TicketingManager.get_new_order_identifier()
        order.event_id = form.get('event_id')
        ticket_ids = form.getlist('rooms[name]')
        ticket_quantity = form.getlist('rooms[floor]')

        for index, id in enumerate(ticket_ids):
            if not string_empty(id) and int(ticket_quantity[index]) > 0:
                order_ticket = OrderTicket()
                order_ticket.ticket = TicketingManager.get_ticket(id)
                order_ticket.quantity = int(ticket_quantity[index])
                order.tickets.append(order_ticket)

        save_to_db(order)
        return order



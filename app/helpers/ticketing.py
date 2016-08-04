"""Copyright 2016 Niranjan Rajendran"""
import binascii
import os

from datetime import timedelta, datetime

import stripe
from sqlalchemy import func
from flask import url_for


from flask.ext import login
from app.helpers.data import save_to_db
from app.helpers.helpers import string_empty, send_email_for_after_purchase
from app.models.order import Order
from app.models.ticket import Ticket
from app.helpers.data_getter import DataGetter
from app.helpers.data import DataManager

from app.models.ticket_holder import TicketHolder
from app.models.order import OrderTicket
from app.models.event import Event
from app.models.user_detail import UserDetail
from app.helpers.helpers import send_email_after_account_create_with_password


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
    def get_orders_of_user(user_id=None, upcoming_events=True):
        """
        :return: Return all order objects with the current user
        """
        if not user_id:
            user_id = login.current_user.id
        if upcoming_events:
            return Order.query.join(Order.event).filter(Order.user_id == user_id)\
                .filter(Order.status == 'completed')\
                .filter(Event.start_time >= datetime.now())
        else:
            return Order.query.join(Order.event).filter(Order.user_id == user_id)\
                .filter(Order.status == 'completed')\
                .filter(Event.end_time < datetime.now())

    @staticmethod
    def get_orders(event_id=None, status=None):
        if event_id:
            if status:
                orders = Order.query.filter_by(event_id=event_id).filter_by(status=status).all()
            else:
                orders = Order.query.filter_by(event_id=event_id).all()
        else:
            if status:
                orders = Order.query.filter_by(status=status).all()
            else:
                orders = Order.query.all()
        return orders

    @staticmethod
    def get_orders_count(event_id, status='completed'):
        return get_count(Order.query.filter_by(event_id=event_id).filter_by(status=status))

    @staticmethod
    def get_orders_count_by_type(event_id, type='free'):
        return get_count(Order.query.filter_by(event_id=event_id).filter_by(status='completed').filter(Ticket.type == type))

    @staticmethod
    def get_all_orders_count_by_type(type='free'):
        return get_count(Order.query.filter_by(status='completed').filter(Ticket.type == type))

    @staticmethod
    def get_max_orders_count(event_id, type='free'):
        ticket = Ticket.query.filter_by(event_id=event_id).filter_by(type=type).first()
        if ticket:
            return ticket.quantity
        else:
            return 0

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
        return Order.query.filter_by(identifier=identifier).first()

    @staticmethod
    def get_or_create_user_by_email(email, data=None):
        user = DataGetter.get_user_by_email(email, False)
        if not user:
            password = binascii.b2a_hex(os.urandom(4))
            user_data = [email, password]
            user = DataManager.create_user(user_data)
            send_email_after_account_create_with_password({
                'email': email,
                'password': password
            })
        if user.user_detail:
            user.user_detail.fullname = data['firstname'] + ' ' + data['lastname']
        else:
            user_detail = UserDetail(fullname=data['firstname'] + ' ' + data['lastname'])
            user.user_detail = user_detail

        save_to_db(user)
        return user

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
                or (order.status != 'completed' and
                    (order.created_at + timedelta(minutes=TicketingManager.get_order_expiry())) < datetime.utcnow()):
                order.status = 'expired'
                save_to_db(order)
        return order

    @staticmethod
    def create_order(form):
        order = Order()
        order.status = 'pending'
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

    @staticmethod
    def initiate_order_payment(form):
        identifier = form['identifier']
        email = form['email']

        order = TicketingManager.get_and_set_expiry(identifier)

        if order:

            user = TicketingManager.get_or_create_user_by_email(email, form)
            order.user_id = user.id

            if order.amount > 0:
                country = form['country']
                address = form['address']
                city = form['city']
                state = form['state']
                zipcode = form['zipcode']
                order.address = address
                order.city = city
                order.state = state
                order.country = country
                order.zipcode = zipcode
                order.status = 'initialized'
                ticket_holder = TicketHolder(name=user.user_detail.fullname,
                                             email=email, address=address,
                                             city=city, state=state, country=country, order_id=order.id)
            else:
                order.status = 'completed'
                order.completed_at = datetime.utcnow()
                ticket_holder = TicketHolder(name=user.user_detail.fullname, email=email, order_id=order.id)

            save_to_db(order)
            save_to_db(ticket_holder)

            return order
        else:
            return False

    @staticmethod
    def charge_order_payment(form):
        order = TicketingManager.get_and_set_expiry(form['identifier'])
        order.token = form['stripe_token_id']
        save_to_db(order)
        try:
            customer = stripe.Customer.create(
                email=order.user.email,
                source=form['stripe_token_id']
            )

            charge = stripe.Charge.create(
                customer=customer.id,
                amount=int(order.amount * 100),
                currency='usd',
                metadata={
                    'order_id': order.id,
                    'event': order.event.name,
                    'user_id': order.user_id,
                    'event_id': order.event_id
                },
                description=order.event.name + " ticket(s)"
            )

            if charge:
                order.paid_via = 'stripe'
                order.payment_mode = charge.source.object
                order.brand = charge.source.brand
                order.exp_month = charge.source.exp_month
                order.exp_year = charge.source.exp_year
                order.last4 = charge.source.last4
                order.transaction_id = charge.id
                order.status = 'completed'
                order.completed_at = datetime.utcnow()
                save_to_db(order)

                send_email_for_after_purchase(order.user.email, order.get_invoice_number(),
                                              url_for('ticketing.view_order_after_payment',
                                                      order_identifier=order.identifier, _external=True))

                return order
            else:
                return False

        except:
            return False

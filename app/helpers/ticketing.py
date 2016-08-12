"""Copyright 2016 Niranjan Rajendran"""
import binascii
import os
import uuid

from datetime import timedelta, datetime

from flask import url_for

from flask.ext import login
from app.helpers.data import save_to_db
from app.helpers.helpers import string_empty, send_email_for_after_purchase, get_count
from app.models.order import Order
from app.models.ticket import Ticket
from app.helpers.data_getter import DataGetter
from app.helpers.data import DataManager

from app.helpers.payment import StripePaymentsManager, represents_int, PayPalPaymentsManager
from app.models.ticket_holder import TicketHolder
from app.models.order import OrderTicket
from app.models.event import Event
from app.models.user_detail import UserDetail
from app.models.discount_code import DiscountCode

from app.helpers.helpers import send_email_after_account_create_with_password


class TicketingManager(object):
    """All ticketing and orders related functions"""

    @staticmethod
    def get_orders_of_user(user_id=None, upcoming_events=True):
        """
        :return: Return all order objects with the current user
        """
        if not user_id:
            user_id = login.current_user.id
        query = Order.query.join(Order.event) \
            .filter(Order.user_id == user_id) \
            .filter(Order.status == 'completed')
        if upcoming_events:
            return query.filter(Event.start_time >= datetime.now())
        else:
            return query.filter(Event.end_time < datetime.now())

    @staticmethod
    def get_orders(event_id=None, status=None):
        if event_id:
            if status:
                orders = Order.query.filter_by(event_id=event_id).filter_by(status=status) \
                    .filter(Order.user_id.isnot(None)).all()
            else:
                orders = Order.query.filter_by(event_id=event_id).filter(Order.user_id.isnot(None)).all()
        else:
            if status:
                orders = Order.query.filter_by(status=status).filter(Order.user_id.isnot(None)).all()
            else:
                orders = Order.query.filter(Order.user_id.isnot(None)).all()
        return orders

    @staticmethod
    def get_orders_count(event_id, status='completed'):
        return get_count(Order.query.filter_by(event_id=event_id).filter(Order.user_id.isnot(None))
                         .filter_by(status=status))

    @staticmethod
    def get_orders_count_by_type(event_id, type='free'):
        return get_count(Order.query.filter_by(event_id=event_id).filter_by(status='completed')
                         .filter(Ticket.type == type))

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
        identifier = str(uuid.uuid4())
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
    def get_discount_codes(event_id):
        return DiscountCode.query.filter_by(event_id=event_id).all()

    @staticmethod
    def get_discount_code(event_id, discount_code):
        if represents_int(discount_code):
            return DiscountCode.query.get(discount_code)
        else:
            return DiscountCode.query.filter_by(code=discount_code).first()

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
            user.user_detail.firstname = data['firstname']
            user.user_detail.lastname = data['lastname']
        else:
            user_detail = UserDetail(firstname=data['firstname'], lastname=data['lastname'])
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

        if order and not order.paid_via:
            if override \
                or (order.status != 'completed' and
                            (order.created_at + timedelta(
                                minutes=TicketingManager.get_order_expiry())) < datetime.utcnow()):
                order.status = 'expired'
                save_to_db(order)
        return order

    @staticmethod
    def create_order(form, from_organizer=False):
        order = Order()
        order.status = 'pending'
        order.identifier = TicketingManager.get_new_order_identifier()
        order.event_id = form.get('event_id')

        if from_organizer:
            order.paid_via = form.get('payment_via')

        ticket_ids = form.getlist('ticket_ids[]')
        ticket_quantity = form.getlist('ticket_quantities[]')

        ticket_subtotals = []
        if from_organizer:
            ticket_subtotals = form.getlist('ticket_subtotals[]')

        amount = 0
        for index, id in enumerate(ticket_ids):
            if not string_empty(id) and int(ticket_quantity[index]) > 0:
                order_ticket = OrderTicket()
                order_ticket.ticket = TicketingManager.get_ticket(id)
                order_ticket.quantity = int(ticket_quantity[index])
                order.tickets.append(order_ticket)

                if from_organizer:
                    amount += int(ticket_subtotals[index])
                else:
                    amount += (order_ticket.ticket.price * order_ticket.quantity)

        order.amount = amount

        if login.current_user.is_authenticated:
            order.user_id = login.current_user.id

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

            if order.amount > 0 \
                and (not order.paid_via
                     or (order.paid_via
                         and (order.paid_via == 'stripe'
                              or order.paid_via == 'paypal'))):

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
                if not order.paid_via:
                    order.paid_via = 'free'
                ticket_holder = TicketHolder(name=user.user_detail.fullname, email=email, order_id=order.id)
            # add attendee role to user
            DataManager.add_attendee_role_to_event(user, order.event_id)
            # save items
            save_to_db(order)
            save_to_db(ticket_holder)

            return order
        else:
            return False

    @staticmethod
    def charge_stripe_order_payment(form):
        order = TicketingManager.get_and_set_expiry(form['identifier'])
        order.stripe_token = form['stripe_token_id']
        save_to_db(order)

        charge = StripePaymentsManager.capture_payment(order)
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
            return True, order
        else:
            return False, 'Error'

    @staticmethod
    def charge_paypal_order_payment(order):
        payment_details = PayPalPaymentsManager.get_approved_payment_details(order)
        if 'PAYERID' in payment_details:
            capture_result = PayPalPaymentsManager.capture_payment(order, payment_details['PAYERID'])
            if capture_result['ACK'] == 'Success':
                order.paid_via = 'paypal'
                order.status = 'completed'
                order.transaction_id = capture_result['PAYMENTINFO_0_TRANSACTIONID']
                order.completed_at = datetime.utcnow()
                save_to_db(order)
                send_email_for_after_purchase(order.user.email, order.get_invoice_number(),
                                              url_for('ticketing.view_order_after_payment',
                                                      order_identifier=order.identifier, _external=True))
                return True, order
            else:
                return False, capture_result['L_SHORTMESSAGE0']
        else:
            return False, 'Payer ID missing. Payment flow tampered.'

    @staticmethod
    def create_edit_discount_code(form, event_id, discount_code_id=None):
        if not discount_code_id:
            discount_code = DiscountCode()
        else:
            discount_code = TicketingManager.get_discount_code(event_id, discount_code_id)
        discount_code.code = form.get('code')
        discount_code.value = form.get('value')
        discount_code.type = form.get('value_type')
        discount_code.min_quantity = form.get('min_quantity', None)
        discount_code.max_quantity = form.get('max_quantity', None)
        discount_code.tickets_number = form.get('tickets_number')
        discount_code.event_id = event_id

        if discount_code.min_quantity == "":
            discount_code.min_quantity = None
        if discount_code.max_quantity == "":
            discount_code.max_quantity = None
        if discount_code.tickets_number == "":
            discount_code.tickets_number = None

        try:
            discount_code.valid_from = datetime.strptime(form.get('start_date', None) + ' ' +
                                                         form.get('start_time', None), '%m/%d/%Y %H:%M')
        except:
            discount_code.valid_from = None

        try:
            discount_code.valid_till = datetime.strptime(form.get('end_date', None) + ' ' +
                                                         form.get('end_time', None), '%m/%d/%Y %H:%M')
        except:
            discount_code.valid_till = None

        discount_code.tickets = ",".join(form.getlist('tickets[]'))

        save_to_db(discount_code)

        return discount_code

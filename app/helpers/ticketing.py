import uuid
from datetime import timedelta, datetime

from flask import url_for, flash
from flask.ext import login
from sqlalchemy import desc
from sqlalchemy import or_

from app.helpers.cache import cache
from app.helpers.data import DataManager
from app.helpers.data import save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import string_empty, send_email_for_after_purchase, get_count, \
    send_notif_for_after_purchase, send_email_after_cancel_ticket
from app.helpers.notification_email_triggers import trigger_after_purchase_notifications
from app.helpers.payment import StripePaymentsManager, represents_int, PayPalPaymentsManager
from app.models import db
from app.models.access_code import AccessCode
from app.models.discount_code import DiscountCode, TICKET
from app.models.event import Event
from app.models.order import Order
from app.models.order import OrderTicket
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder


class TicketingManager(object):
    """All ticketing and orders related functions"""

    @staticmethod
    @cache.memoize(50)
    def get_ticket(ticket_id):
        return Ticket.query.get(ticket_id)

    @staticmethod
    def get_orders_of_user(user_id=None, upcoming_events=True):
        """
        :return: Return all order objects with the current user
        """
        if not user_id:
            user_id = login.current_user.id
        query = Order.query.join(Order.event) \
            .filter(Order.user_id == user_id) \
            .filter(or_(Order.status == 'completed', Order.status == 'placed'))
        if upcoming_events:
            return query.filter(Event.start_time >= datetime.now())
        else:
            return query.filter(Event.end_time < datetime.now())

    @staticmethod
    def get_orders(event_id=None, status=None, from_date=None, to_date=None, marketer_id=None, promoted_event=False):
        if event_id:
            if status:
                orders = Order.query.filter_by(event_id=event_id).filter_by(status=status) \
                    .filter(Order.user_id.isnot(None))
            else:
                orders = Order.query.filter_by(event_id=event_id).filter(Order.user_id.isnot(None))
        else:
            if status:
                orders = Order.query.filter_by(status=status).filter(Order.user_id.isnot(None))
            else:
                orders = Order.query.filter(Order.user_id.isnot(None))

        if from_date:
            orders = orders.filter(Order.created_at >= from_date)
        if to_date:
            orders = orders.filter(Order.created_at <= to_date)

        if promoted_event:
            orders = orders.join(Order.event).filter(Event.discount_code_id != None)

        orders = orders.order_by(desc(Order.id))
        return orders.all()

    @staticmethod
    def get_orders_count(event_id, status='completed'):
        return get_count(Order.query.filter_by(event_id=event_id).filter(Order.user_id.isnot(None))
                         .filter_by(status=status))

    @staticmethod
    def get_orders_count_by_type(event_id, type='free'):
        return get_count(Order.query.filter_by(event_id=event_id).filter_by(status='completed')
                         .filter(Ticket.type == type))

    @staticmethod
    def get_ticket_stats(event):
        tickets_summary = {}
        for ticket in event.tickets:
            tickets_summary[str(ticket.id)] = {
                'name': ticket.name,
                'total': ticket.quantity,
                'completed': 0
            }
        orders = Order.query.filter_by(event_id=event.id).filter(
            or_(Order.status == 'completed', Order.status == 'placed')).all()
        for order in orders:
            for order_ticket in order.tickets:
                tickets_summary[str(order_ticket.ticket_id)]['completed'] += order_ticket.quantity
        return tickets_summary

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
    def get_attendee(id):
        holder = None
        if represents_int(id):
            holder = TicketHolder.query.get(id)
        else:
            id_splitted = id.split("/")
            order_identifier = id_splitted[0]
            holder_id = id_splitted[1]
            order = TicketingManager.get_order_by_identifier(order_identifier)
            attendee = TicketingManager.get_attendee(holder_id)
            if attendee.order_id == order.id:
                holder = attendee
        return holder

    @staticmethod
    def get_attendees(event_id):
        return TicketHolder.query.join(TicketHolder.order, aliased=True) \
            .filter(Order.status == 'completed').filter(Order.event_id == event_id).all()

    @staticmethod
    def attendee_check_in_out(id, state=None):
        holder = TicketingManager.get_attendee(id)
        if holder:
            if state is not None:
                holder.checked_in = state
            else:
                holder.checked_in = not holder.checked_in
            save_to_db(holder)
            return holder
        else:
            return None

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
    def get_order(order_id):
        return Ticket.query.get(order_id)

    @staticmethod
    def get_order_by_identifier(identifier):
        return Order.query.filter_by(identifier=identifier).first()

    @staticmethod
    def get_discount_codes(event_id):
        return DiscountCode.query.filter_by(event_id=event_id).filter_by(used_for=TICKET).all()

    @staticmethod
    def get_discount_code(event_id, discount_code):
        if represents_int(discount_code):
            return DiscountCode.query \
                .filter_by(id=discount_code) \
                .filter_by(event_id=event_id) \
                .filter_by(used_for=TICKET).first()
        else:
            return DiscountCode.query \
                .filter_by(code=discount_code) \
                .filter_by(event_id=event_id) \
                .filter_by(used_for=TICKET).first()

    @staticmethod
    def get_access_codes(event_id):
        return AccessCode.query.filter_by(event_id=event_id).filter_by(used_for=TICKET).all()

    @staticmethod
    def get_access_code(event_id, access_code):
        if represents_int(access_code):
            return AccessCode.query \
                .filter_by(id=access_code) \
                .filter_by(event_id=event_id) \
                .filter_by(used_for=TICKET).first()
        else:
            return AccessCode.query \
                .filter_by(code=access_code) \
                .filter_by(event_id=event_id) \
                .filter_by(used_for=TICKET).first()

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
                or (order.status != 'completed' and order.status != 'placed' and
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
        ticket_discount = form.get('promo_code', '')
        discount = None
        if ticket_discount:
            discount = TicketingManager.get_discount_code(form.get('event_id'), form.get('promo_code', ''))
            access_code = TicketingManager.get_access_code(form.get('event_id'), form.get('promo_code', ''))
            if access_code and discount:
                order.discount_code = discount
                flash('Both access code and discount code have been applied. You can make this order now.', 'success')
            elif discount:
                order.discount_code = discount
                flash('The promotional code entered is valid. Offer has been applied to this order.', 'success')
            elif access_code:
                flash('Your access code is applied and you can make this order now.', 'success')
            else:
                flash('The promotional code entered is not valid. No offer has been applied to this order.', 'danger')

        ticket_subtotals = []
        if from_organizer:
            ticket_subtotals = form.getlist('ticket_subtotals[]')

        amount = 0
        total_discount = 0
        fees = DataGetter.get_fee_settings_by_currency(DataGetter.get_event(order.event_id).payment_currency)
        for index, id in enumerate(ticket_ids):
            if not string_empty(id) and int(ticket_quantity[index]) > 0:
                with db.session.no_autoflush:
                    order_ticket = OrderTicket()
                    order_ticket.ticket = TicketingManager.get_ticket(id)
                    order_ticket.quantity = int(ticket_quantity[index])
                    order.tickets.append(order_ticket)

                    if order_ticket.ticket.absorb_fees or not fees:
                        ticket_amount = (order_ticket.ticket.price * order_ticket.quantity)
                        amount += (order_ticket.ticket.price * order_ticket.quantity)
                    else:
                        order_fee = fees.service_fee * (order_ticket.ticket.price * order_ticket.quantity) / 100
                        if order_fee > fees.maximum_fee:
                            ticket_amount = (order_ticket.ticket.price * order_ticket.quantity) + fees.maximum_fee
                            amount += (order_ticket.ticket.price * order_ticket.quantity) + fees.maximum_fee
                        else:
                            ticket_amount = (order_ticket.ticket.price * order_ticket.quantity) + order_fee
                            amount += (order_ticket.ticket.price * order_ticket.quantity) + order_fee

                    if from_organizer:
                        amount += float(ticket_subtotals[index])
                    else:
                        if discount and str(order_ticket.ticket.id) in discount.tickets.split(","):
                            if discount.type == "amount":
                                total_discount += discount.value * order_ticket.quantity
                            else:
                                total_discount += discount.value * ticket_amount / 100

        if discount:
            order.amount = max(amount - total_discount, 0)
        elif discount:
            order.amount = amount - (discount.value * amount / 100.0)
        else:
            order.amount = amount

        if login.current_user.is_authenticated:
            order.user_id = login.current_user.id

        save_to_db(order)
        return order

    @staticmethod
    def initiate_order_payment(form, paid_via=None):
        identifier = form['identifier']
        email = form['email']

        order = TicketingManager.get_and_set_expiry(identifier)

        if order:
            user = DataGetter.get_or_create_user_by_email(email, form)
            order.user_id = user.id

            if order.amount > 0 \
                and (not order.paid_via
                     or (order.paid_via
                         and (order.paid_via == 'stripe'
                              or order.paid_via == 'paypal'))):

                if paid_via:
                    order.paid_via = paid_via

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

                if paid_via == 'transfer' or paid_via == 'onsite' or paid_via == 'cheque':
                    order.status = 'placed'
                else:
                    order.status = 'initialized'

            else:
                order.status = 'completed'
                order.completed_at = datetime.utcnow()
                if not order.paid_via:
                    order.paid_via = 'free'

            invoice_id = order.get_invoice_number()
            order_url = url_for('ticketing.view_order_after_payment',
                                order_identifier=order.identifier,
                                _external=True)

            # add holders to user
            holders_firstnames = form.getlist('holders[firstname]')
            holders_lastnames = form.getlist('holders[lastname]')
            holders_ticket_ids = form.getlist('holders[ticket_id]')
            holders_emails = form.getlist('holders[email]')

            for i, firstname in enumerate(holders_firstnames):
                data = {
                    'firstname': firstname,
                    'lastname': holders_lastnames[i]
                }
                holder_user = DataGetter.get_or_create_user_by_email(holders_emails[i], data)
                ticket_holder = TicketHolder(firstname=data['firstname'],
                                             lastname=data['lastname'],
                                             ticket_id=int(holders_ticket_ids[i]),
                                             email=holder_user.email,
                                             order_id=order.id)
                if order.status == "completed":
                    send_email_for_after_purchase(holder_user.email, invoice_id, order_url, order.event.name,
                                                  order.event.organizer_name)
                DataManager.add_attendee_role_to_event(holder_user, order.event_id)
                db.session.add(ticket_holder)

            # add attendee role to user
            if order.status == "completed":
                trigger_after_purchase_notifications(email, order.event_id, order.event, invoice_id, order_url)
                send_email_for_after_purchase(email, invoice_id, order_url, order.event.name,
                                              order.event.organizer_name)
            DataManager.add_attendee_role_to_event(user, order.event_id)
            # save items
            save_to_db(order)
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

            invoice_id = order.get_invoice_number()
            order_url = url_for('ticketing.view_order_after_payment',
                                order_identifier=order.identifier,
                                _external=True)
            trigger_after_purchase_notifications(order.user.email, order.event_id, order.event, invoice_id, order_url)
            send_email_for_after_purchase(order.user.email, invoice_id, order_url, order.event.name,
                                          order.event.organizer_name)
            send_notif_for_after_purchase(order.user, invoice_id, order_url)

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

                invoice_id = order.get_invoice_number()
                order_url = url_for('ticketing.view_order_after_payment',
                                    order_identifier=order.identifier,
                                    _external=True)
                trigger_after_purchase_notifications(order.user.email, order.event_id, order.event, invoice_id,
                                                     order_url)
                send_email_for_after_purchase(order.user.email, invoice_id, order_url, order.event.name,
                                              order.event.organizer_name)
                send_notif_for_after_purchase(order.user, invoice_id, order_url)

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
        discount_code.discount_url = form.get('discount_url')
        discount_code.min_quantity = form.get('min_quantity', None)
        discount_code.max_quantity = form.get('max_quantity', None)
        discount_code.tickets_number = form.get('tickets_number')
        discount_code.event_id = event_id
        discount_code.used_for = TICKET
        discount_code.is_active = form.get('status', 'in_active') == 'active'

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

    @staticmethod
    def create_edit_access_code(form, event_id, access_code_id=None):
        if not access_code_id:
            access_code = AccessCode()
        else:
            access_code = TicketingManager.get_access_code(event_id, access_code_id)
        access_code.code = form.get('code')
        access_code.access_url = form.get('access_url')
        access_code.min_quantity = form.get('min_quantity', None)
        access_code.max_quantity = form.get('max_quantity', None)
        access_code.tickets_number = form.get('tickets_number')
        access_code.event_id = event_id
        access_code.used_for = TICKET
        access_code.is_active = form.get('status', 'in_active') == 'active'

        if access_code.min_quantity == "":
            access_code.min_quantity = None
        if access_code.max_quantity == "":
            access_code.max_quantity = None
        if access_code.tickets_number == "":
            access_code.tickets_number = None

        try:
            access_code.valid_from = datetime.strptime(form.get('start_date', None) + ' ' +
                                                       form.get('start_time', None), '%m/%d/%Y %H:%M')
        except:
            access_code.valid_from = None

        try:
            access_code.valid_till = datetime.strptime(form.get('end_date', None) + ' ' +
                                                       form.get('end_time', None), '%m/%d/%Y %H:%M')
        except:
            access_code.valid_till = None

        access_code.tickets = ",".join(form.getlist('tickets[]'))

        save_to_db(access_code)

        return access_code

    @staticmethod
    def cancel_order(form):
        order = TicketingManager.get_and_set_expiry(form.get('identifier'))
        event_id = order.event_id
        event_name = order.event.name
        invoice_id = order.get_invoice_number()
        order_url = url_for('ticketing.view_order_after_payment', order_identifier=order.identifier, _external=True)
        user = DataGetter.get_user(order.user_id)
        if login.current_user.is_organizer(event_id):
            order.status = "cancelled"
            save_to_db(order)
            send_email_after_cancel_ticket(user.email, invoice_id, order_url, event_name, form.get('note'))
            return True
        return False

    @staticmethod
    def delete_order(form):
        order = TicketingManager.get_and_set_expiry(form.get('identifier'))
        event_id = order.event_id
        if login.current_user.is_organizer(event_id):
            if order.status != "deleted" and (order.amount == 0 or order.status != "completed"):
                order.trashed_at = datetime.now()
                order.status = "deleted"
                save_to_db(order)
            return True
        return False

    @staticmethod
    def resend_confirmation(form):
        order = TicketingManager.get_and_set_expiry(form.get('identifier'))
        email = form.get('email')
        event_id = order.event_id
        invoice_id = order.get_invoice_number()
        order_url = url_for('ticketing.view_order_after_payment', order_identifier=order.identifier, _external=True)
        if login.current_user.is_organizer(event_id):
            trigger_after_purchase_notifications(email, order.event_id, order.event, invoice_id, order_url)
            send_email_for_after_purchase(email, invoice_id, order_url, order.event.name, order.event.organizer_name)
            return True
        return False

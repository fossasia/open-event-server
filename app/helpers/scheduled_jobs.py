from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from flask import url_for
from sqlalchemy_continuum import transaction_class

from app.helpers.helpers import send_after_event, monthdelta, send_followup_email_for_monthly_fee_payment
from app.helpers.helpers import send_email_for_expired_orders, send_email_for_monthly_fee_payment
from app.helpers.data import DataManager, delete_from_db, save_to_db
from app.helpers.data_getter import DataGetter
from app.helpers.payment import get_fee
from app.helpers.ticketing import TicketingManager
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.user import User
from flask import current_app as app

def empty_trash():
    with app.app_context():
        events = Event.query.filter_by(in_trash=True)
        users = User.query.filter_by(in_trash=True)
        sessions = Session.query.filter_by(in_trash=True)
        for event in events:
            if datetime.now() - event.trash_date >= timedelta(days=30):
                DataManager.delete_event(event.id)

        for user in users:
            if datetime.now() - user.trash_date >= timedelta(days=30):
                transaction = transaction_class(Event)
                transaction.query.filter_by(user_id=user.id).delete()
                delete_from_db(user, "User deleted permanently")

        for session_ in sessions:
            if datetime.now() - session_.trash_date >= timedelta(days=30):
                delete_from_db(session_, "Session deleted permanently")

def send_after_event_mail():
    with app.app_context():
        events = Event.query.all()
        for event in events:
            upcoming_events = DataGetter.get_upcoming_events(event.id)
            organizers = DataGetter.get_user_event_roles_by_role_name(
                event.id, 'organizer')
            speakers = DataGetter.get_user_event_roles_by_role_name(event.id,
                                                                    'speaker')
            if datetime.now() > event.end_time:
                for speaker in speakers:
                    send_after_event(speaker.user.email, event.id,
                                     upcoming_events)
                for organizer in organizers:
                    send_after_event(organizer.user.email, event.id,
                                     upcoming_events)


def send_mail_to_expired_orders():
    with app.app_context():
        orders = DataGetter.get_expired_orders()
        for order in orders:
            send_email_for_expired_orders(order.user.email, order.event.name, order.get_invoice_number(),
                                          url_for('ticketing.view_order_after_payment',
                                                  order_identifier=order.identifier, _external=True))

def send_event_fee_notification():
    with app.app_context():
        events = Event.query.all()
        for event in events:
            latest_invoice = EventInvoice.filter_by(event_id=event.id).order_by(EventInvoice.created_at.desc()).first()

            if latest_invoice:
                orders = Order.query\
                    .filter_by(event_id=event.id)\
                    .filter_by(status='completed')\
                    .filter(Order.completed_at > latest_invoice.created_at).all()
            else:
                orders = Order.query.filter_by(event_id=event.id).filter_by(status='completed').all()

            fee_total = 0
            for order in orders:
                for order_ticket in order.tickets:
                    ticket = TicketingManager.get_ticket(order_ticket.ticket_id)
                    if order.paid_via != 'free' and order.amount > 0 and ticket.price > 0:
                        fee = ticket.price * (get_fee(order.event.payment_currency) / 100)
                        fee_total += fee

            if fee_total > 0:
                new_invoice = EventInvoice(amount=fee_total, event_id=event.id, user_id=event.creator_id)

                if event.discount_code_id and event.discount_code:
                    r = relativedelta(datetime.utcnow(), event.created_at)
                    if r <= event.discount_code.max_quantity:
                        new_invoice.amount = fee_total - (fee_total * (event.discount_code.value/100))
                        new_invoice.discount_code_id = event.discount_code_id

                save_to_db(new_invoice)
                prev_month = monthdelta(new_invoice.created_at, 1).strftime("%b %Y")  # Displayed as Aug 2016
                send_email_for_monthly_fee_payment(new_invoice.user.email,
                                                   event.name,
                                                   prev_month,
                                                   new_invoice.amount,
                                                   url_for('event_invoicing.view_invoice',
                                                           invoice_identifier=new_invoice.identifier, _external=True))

def send_event_fee_notification_followup():
    with app.app_context():
        incomplete_invoices = EventInvoice.query.filter(EventInvoice.status != 'completed').all()
        for incomplete_invoice in incomplete_invoices:
            if incomplete_invoice.amount > 0:
                prev_month = monthdelta(incomplete_invoice.created_at, 1).strftime("%b %Y")  # Displayed as Aug 2016
                send_followup_email_for_monthly_fee_payment(incomplete_invoice.user.email,
                                                            incomplete_invoice.event.name,
                                                            prev_month,
                                                            incomplete_invoice.amount,
                                                            url_for('event_invoicing.view_invoice',
                                                                    invoice_identifier=incomplete_invoice.identifier,
                                                                    _external=True))

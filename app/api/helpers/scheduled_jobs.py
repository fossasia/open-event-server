import datetime

import pytz
from dateutil.relativedelta import relativedelta

from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.mail import send_email_after_event, send_email_for_monthly_fee_payment, \
    send_followup_email_for_monthly_fee_payment
from app.api.helpers.notification import send_notif_monthly_fee_payment, send_followup_notif_monthly_fee_payment, \
    send_notif_after_event
from app.api.helpers.query import get_upcoming_events, get_user_event_roles_by_role_name
from app.api.helpers.utilities import monthdelta
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.ticket import Ticket
from app.models.ticket_fee import get_fee
from app.settings import get_settings


def send_after_event_mail():
    from app import current_app as app
    with app.app_context():
        events = Event.query.all()
        upcoming_events = get_upcoming_events()
        upcoming_event_links = "<ul>"
        for upcoming_event in upcoming_events:
            frontend_url = get_settings()['frontend_url']
            upcoming_event_links += "<li><a href='{}/events/{}'>{}</a></li>" \
                .format(frontend_url, upcoming_event.id, upcoming_event.name)
        upcoming_event_links += "</ul>"
        for event in events:
            organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
            speakers = get_user_event_roles_by_role_name(event.id, 'speaker')
            current_time = datetime.datetime.now(pytz.timezone(event.timezone))
            time_difference = current_time - event.ends_at
            time_difference_minutes = (time_difference.days * 24 * 60) + \
                (time_difference.seconds / 60)
            if current_time > event.ends_at and time_difference_minutes < 1440:
                for speaker in speakers:
                    send_email_after_event(speaker.user.email, event.name, upcoming_event_links)
                    send_notif_after_event(speaker.user, event.name)
                for organizer in organizers:
                    send_email_after_event(organizer.user.email, event.name, upcoming_event_links)
                    send_notif_after_event(organizer.user.email, event.name)


def send_event_fee_notification():
    from app import current_app as app
    with app.app_context():
        events = Event.query.all()
        for event in events:
            latest_invoice = EventInvoice.query.filter_by(
                event_id=event.id).order_by(EventInvoice.created_at.desc()).first()

            if latest_invoice:
                orders = Order.query \
                    .filter_by(event_id=event.id) \
                    .filter_by(status='completed') \
                    .filter(Order.completed_at > latest_invoice.created_at).all()
            else:
                orders = Order.query.filter_by(
                    event_id=event.id).filter_by(status='completed').all()

            fee_total = 0
            for order in orders:
                for order_ticket in order.tickets:
                    ticket = safe_query(db, Ticket, 'id', order_ticket.ticket_id, 'ticket_id')
                    if order.paid_via != 'free' and order.amount > 0 and ticket.price > 0:
                        fee = ticket.price * (get_fee(order.event.payment_currency) / 100.0)
                        fee_total += fee

            if fee_total > 0:
                organizer = get_user_event_roles_by_role_name(event.id, 'organizer').first()
                new_invoice = EventInvoice(
                    amount=fee_total, event_id=event.id, user_id=organizer.user.id)

                if event.discount_code_id and event.discount_code:
                    r = relativedelta(datetime.utcnow(), event.created_at)
                    if r <= event.discount_code.valid_till:
                        new_invoice.amount = fee_total - \
                            (fee_total * (event.discount_code.value / 100.0))
                        new_invoice.discount_code_id = event.discount_code_id

                save_to_db(new_invoice)
                prev_month = monthdelta(new_invoice.created_at, 1).strftime(
                    "%b %Y")  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/invoices/{}'.format(frontend_url, new_invoice.identifier)
                send_email_for_monthly_fee_payment(new_invoice.user.email,
                                                   event.name,
                                                   prev_month,
                                                   new_invoice.amount,
                                                   app_name,
                                                   link)
                send_notif_monthly_fee_payment(new_invoice.user,
                                               event.name,
                                               prev_month,
                                               new_invoice.amount,
                                               app_name,
                                               link,
                                               new_invoice.event_id)


def send_event_fee_notification_followup():
    from app import current_app as app
    with app.app_context():
        incomplete_invoices = EventInvoice.query.filter(EventInvoice.status != 'completed').all()
        for incomplete_invoice in incomplete_invoices:
            if incomplete_invoice.amount > 0:
                prev_month = monthdelta(incomplete_invoice.created_at, 1).strftime(
                    "%b %Y")  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/invoices/{}'.format(frontend_url,
                                               incomplete_invoice.identifier)
                send_followup_email_for_monthly_fee_payment(incomplete_invoice.user.email,
                                                            incomplete_invoice.event.name,
                                                            prev_month,
                                                            incomplete_invoice.amount,
                                                            app_name,
                                                            link)
                send_followup_notif_monthly_fee_payment(incomplete_invoice.user,
                                                        incomplete_invoice.event.name,
                                                        prev_month,
                                                        incomplete_invoice.amount,
                                                        app_name,
                                                        link,
                                                        incomplete_invoice.event.id)

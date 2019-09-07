import datetime

import pytz
from dateutil.relativedelta import relativedelta
from flask import render_template

from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.mail import send_email_after_event, send_email_for_monthly_fee_payment, \
    send_followup_email_for_monthly_fee_payment
from app.api.helpers.notification import send_notif_monthly_fee_payment, send_followup_notif_monthly_fee_payment, \
    send_notif_after_event
from app.api.helpers.query import get_upcoming_events, get_user_event_roles_by_role_name
from app.api.helpers.utilities import monthdelta
from app.api.helpers.files import create_save_pdf
from app.api.helpers.storage import UPLOAD_PATHS
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.speaker import Speaker
from app.models.session import Session
from app.models.ticket import Ticket
from app.models.ticket_fee import TicketFees, get_fee

from app.settings import get_settings


def send_after_event_mail():
    from app import current_app as app
    with app.app_context():
        events = Event.query.filter_by(state='published', deleted_at=None).all()
        upcoming_events = get_upcoming_events()
        upcoming_event_links = "<ul>"
        for upcoming_event in upcoming_events:
            frontend_url = get_settings()['frontend_url']
            upcoming_event_links += "<li><a href='{}/events/{}'>{}</a></li>" \
                .format(frontend_url, upcoming_event.id, upcoming_event.name)
        upcoming_event_links += "</ul>"
        for event in events:
            organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
            speakers = Speaker.query.filter_by(event_id=event.id, deleted_at=None).all()
            owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
            current_time = datetime.datetime.now(pytz.timezone(event.timezone))
            time_difference = current_time - event.ends_at
            time_difference_minutes = (time_difference.days * 24 * 60) + \
                (time_difference.seconds / 60)
            if current_time > event.ends_at and time_difference_minutes < 1440:
                for speaker in speakers:
                    if not speaker.is_email_overridden:
                        send_email_after_event(speaker.user.email, event.name, upcoming_event_links)
                        send_notif_after_event(speaker.user, event.name)
                for organizer in organizers:
                    send_email_after_event(organizer.user.email, event.name, upcoming_event_links)
                    send_notif_after_event(organizer.user, event.name)
                if owner:
                    send_email_after_event(owner.user.email, event.name, upcoming_event_links)
                    send_notif_after_event(owner.user, event.name)


def change_session_state_on_event_completion():
    from app import current_app as app
    with app.app_context():
        sessions_to_be_changed = Session.query.join(Event).filter(Session.state == 'pending')\
                                 .filter(Event.ends_at < datetime.datetime.now())
        for session in sessions_to_be_changed:
            session.state = 'rejected'
            save_to_db(session, 'Changed {} session state to rejected'.format(session.title))


def send_event_fee_notification():
    from app import current_app as app
    with app.app_context():
        events = Event.query.filter_by(deleted_at=None, state='published').all()
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
                owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
                new_invoice = EventInvoice(
                    amount=fee_total, event_id=event.id, user_id=owner.user.id)

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
        incomplete_invoices = EventInvoice.query.filter(EventInvoice.status != 'paid').all()
        for incomplete_invoice in incomplete_invoices:
            if incomplete_invoice.amount > 0:
                prev_month = monthdelta(incomplete_invoice.created_at, 1).strftime(
                    "%b %Y")  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/event-invoice/{}/review'.format(frontend_url,
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


def expire_pending_tickets():
    from app import current_app as app
    with app.app_context():
        db.session.query(Order).filter(Order.status == 'pending',
                                       (Order.created_at + datetime.timedelta(minutes=30)) <= datetime.datetime.now()).\
                                       update({'status': 'expired'})
        db.session.commit()


def event_invoices_mark_due():
    from app import current_app as app
    with app.app_context():
        db.session.query(EventInvoice).\
                    filter(EventInvoice.status == 'upcoming',
                           EventInvoice.event.ends_at >= datetime.datetime.now(),
                           (EventInvoice.created_at + datetime.timedelta(days=30) <=
                            datetime.datetime.now())).\
                    update({'status': 'due'})

        db.session.commit()


def send_monthly_event_invoice():
    from app import current_app as app
    with app.app_context():
        events = Event.query.filter_by(deleted_at=None, state='published').all()
        for event in events:
            # calculate net & gross revenues
            user = event.owner
            admin_info = get_settings()
            currency = event.payment_currency
            ticket_fee_object = db.session.query(TicketFees).filter_by(currency=currency).one()
            ticket_fee_percentage = ticket_fee_object.service_fee
            ticket_fee_maximum = ticket_fee_object.maximum_fee
            orders = Order.query.filter_by(event=event).all()
            gross_revenue = event.calc_monthly_revenue()
            ticket_fees = event.tickets_sold * (ticket_fee_percentage / 100)
            if ticket_fees > ticket_fee_maximum:
                ticket_fees = ticket_fee_maximum
            net_revenue = gross_revenue - ticket_fees
            payment_details = {
                'tickets_sold': event.tickets_sold,
                'gross_revenue': gross_revenue,
                'net_revenue': net_revenue,
                'amount_payable': ticket_fees
            }
            # save invoice as pdf
            pdf = create_save_pdf(render_template('pdf/event_invoice.html', orders=orders, user=user,
                                  admin_info=admin_info, currency=currency, event=event,
                                  ticket_fee_object=ticket_fee_object, payment_details=payment_details,
                                  net_revenue=net_revenue), UPLOAD_PATHS['pdf']['event_invoice'],
                                  dir_path='/static/uploads/pdf/event_invoices/', identifier=event.identifier)
            # save event_invoice info to DB

            event_invoice = EventInvoice(amount=net_revenue, invoice_pdf_url=pdf, event_id=event.id)
            save_to_db(event_invoice)

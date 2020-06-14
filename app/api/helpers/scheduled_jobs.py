import datetime
import logging

import pytz
from dateutil.relativedelta import relativedelta
from flask import render_template
from flask_celeryext import RequestContextTask
from sqlalchemy.orm.exc import NoResultFound

from app.api.helpers.db import save_to_db
from app.api.helpers.files import create_save_pdf
from app.api.helpers.mail import (
    send_email_after_event,
    send_email_for_monthly_fee_payment,
    send_followup_email_for_monthly_fee_payment,
)
from app.api.helpers.notification import (
    send_followup_notif_monthly_fee_payment,
    send_notif_after_event,
    send_notif_monthly_fee_payment,
)
from app.api.helpers.query import get_user_event_roles_by_role_name
from app.api.helpers.storage import UPLOAD_PATHS
from app.api.helpers.utilities import monthdelta
from app.instance import celery
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket_fee import TicketFees, get_fee
from app.models.ticket_holder import TicketHolder
from app.settings import get_settings

logger = logging.getLogger(__name__)


@celery.task(base=RequestContextTask, name='send.after.event.mail')
def send_after_event_mail():
    from app.instance import current_app as app

    with app.app_context():
        events = Event.query.filter_by(state='published', deleted_at=None).all()
        for event in events:
            organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
            speakers = Speaker.query.filter_by(event_id=event.id, deleted_at=None).all()
            owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
            current_time = datetime.datetime.now(pytz.timezone(event.timezone))
            time_difference = current_time - event.ends_at
            time_difference_minutes = (time_difference.days * 24 * 60) + (
                time_difference.seconds / 60
            )
            frontend_url = get_settings()['frontend_url']
            if current_time > event.ends_at and time_difference_minutes < 1440:
                for speaker in speakers:
                    if not speaker.is_email_overridden:
                        send_email_after_event(
                            speaker.user.email, event.name, frontend_url
                        )
                        send_notif_after_event(speaker.user, event.name)
                for organizer in organizers:
                    send_email_after_event(organizer.user.email, event.name, frontend_url)
                    send_notif_after_event(organizer.user, event.name)
                if owner:
                    send_email_after_event(owner.user.email, event.name, frontend_url)
                    send_notif_after_event(owner.user, event.name)


@celery.task(base=RequestContextTask, name='change.session.state.on.event.completion')
def change_session_state_on_event_completion():
    from app.instance import current_app as app

    with app.app_context():
        sessions_to_be_changed = (
            Session.query.join(Event)
            .filter(Session.state == 'pending')
            .filter(Event.ends_at < datetime.datetime.now())
        )
        for session in sessions_to_be_changed:
            session.state = 'rejected'
            save_to_db(
                session, 'Changed {} session state to rejected'.format(session.title)
            )


@celery.task(base=RequestContextTask, name='send.event.fee.notification')
def send_event_fee_notification():
    from app.instance import current_app as app

    with app.app_context():
        events = Event.query.filter_by(deleted_at=None, state='published').all()
        for event in events:
            latest_invoice = (
                EventInvoice.query.filter_by(event_id=event.id)
                .order_by(EventInvoice.created_at.desc())
                .first()
            )

            if latest_invoice:
                orders = (
                    Order.query.filter_by(event_id=event.id)
                    .filter_by(status='completed')
                    .filter(Order.completed_at > latest_invoice.created_at)
                    .all()
                )
            else:
                orders = (
                    Order.query.filter_by(event_id=event.id)
                    .filter_by(status='completed')
                    .all()
                )

            fee_total = 0
            for order in orders:
                for ticket in order.tickets:
                    if order.paid_via != 'free' and order.amount > 0 and ticket.price > 0:
                        fee = ticket.price * (
                            get_fee(event.payment_country, order.event.payment_currency)
                            / 100.0
                        )
                        fee_total += fee

            if fee_total > 0:
                owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
                new_invoice = EventInvoice(
                    amount=fee_total, event_id=event.id, user_id=owner.user.id
                )

                if event.discount_code_id and event.discount_code:
                    r = relativedelta(datetime.datetime.utcnow(), event.created_at)
                    if r <= event.discount_code.valid_till:
                        new_invoice.amount = fee_total - (
                            fee_total * (event.discount_code.value / 100.0)
                        )
                        new_invoice.discount_code_id = event.discount_code_id

                save_to_db(new_invoice)
                prev_month = monthdelta(new_invoice.created_at, 1).strftime(
                    "%b %Y"
                )  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/invoices/{}'.format(frontend_url, new_invoice.identifier)
                send_email_for_monthly_fee_payment(
                    new_invoice.user.email,
                    event.name,
                    prev_month,
                    new_invoice.amount,
                    app_name,
                    link,
                )
                send_notif_monthly_fee_payment(
                    new_invoice.user,
                    event.name,
                    prev_month,
                    new_invoice.amount,
                    app_name,
                    link,
                    new_invoice.event_id,
                )


@celery.task(base=RequestContextTask, name='send.event.fee.notification.followup')
def send_event_fee_notification_followup():
    from app.instance import current_app as app

    with app.app_context():
        incomplete_invoices = EventInvoice.query.filter(
            EventInvoice.status != 'paid'
        ).all()
        for incomplete_invoice in incomplete_invoices:
            if incomplete_invoice.amount > 0:
                prev_month = monthdelta(incomplete_invoice.created_at, 1).strftime(
                    "%b %Y"
                )  # Displayed as Aug 2016
                app_name = get_settings()['app_name']
                frontend_url = get_settings()['frontend_url']
                link = '{}/event-invoice/{}/review'.format(
                    frontend_url, incomplete_invoice.identifier
                )
                send_followup_email_for_monthly_fee_payment(
                    incomplete_invoice.user.email,
                    incomplete_invoice.event.name,
                    prev_month,
                    incomplete_invoice.amount,
                    app_name,
                    link,
                )
                send_followup_notif_monthly_fee_payment(
                    incomplete_invoice.user,
                    incomplete_invoice.event.name,
                    prev_month,
                    incomplete_invoice.amount,
                    app_name,
                    link,
                    incomplete_invoice.event.id,
                )


@celery.task(base=RequestContextTask, name='expire.pending.tickets')
def expire_pending_tickets():
    Order.query.filter(
        Order.status == 'pending',
        (Order.created_at + datetime.timedelta(minutes=30))
        <= datetime.datetime.now(datetime.timezone.utc),
    ).update({'status': 'expired'})
    db.session.commit()


@celery.task(base=RequestContextTask, name='expire.initializing.tickets')
def expire_initializing_tickets():
    order_expiry_time = get_settings()['order_expiry_time']
    query = db.session.query(Order.id).filter(
        Order.status == 'initializing',
        Order.paid_via == None,
        (Order.created_at + datetime.timedelta(minutes=order_expiry_time))
        <= datetime.datetime.now(datetime.timezone.utc),
    )
    # pytype: disable=attribute-error
    TicketHolder.query.filter(TicketHolder.order_id.in_(query.subquery())).delete(
        synchronize_session=False
    )
    # pytype: enable=attribute-error
    query.update({'status': 'expired'})

    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


@celery.task(base=RequestContextTask, name='delete.ticket.holders.no.order.id')
def delete_ticket_holders_no_order_id():
    order_expiry_time = get_settings()['order_expiry_time']
    TicketHolder.query.filter(
        TicketHolder.order_id == None,
        TicketHolder.deleted_at.is_(None),
        TicketHolder.created_at + datetime.timedelta(minutes=order_expiry_time)
        < datetime.datetime.utcnow(),
    ).delete(synchronize_session=False)
    db.session.commit()


@celery.task(base=RequestContextTask, name='event.invoices.mark.due')
def event_invoices_mark_due():
    db.session.query(EventInvoice).filter(
        EventInvoice.status == 'upcoming',
        Event.id == EventInvoice.event_id,
        Event.ends_at >= datetime.datetime.now(),
        (
            EventInvoice.created_at + datetime.timedelta(days=30)
            <= datetime.datetime.now()
        ),
    ).update({EventInvoice.status: 'due'}, synchronize_session=False)


@celery.task(base=RequestContextTask, name='send.monthly.event.invoice')
def send_monthly_event_invoice():
    events = Event.query.filter_by(deleted_at=None, state='published').all()

    for event in events:
        # calculate net & gross revenues
        user = event.owner
        admin_info = get_settings()
        currency = event.payment_currency
        try:
            ticket_fee_object = (
                db.session.query(TicketFees).filter_by(currency=currency).one()
            )
        except NoResultFound:
            logger.error('Ticket Fee not found for event id {id}'.format(id=event.id))
            continue

        ticket_fee_percentage = ticket_fee_object.service_fee
        ticket_fee_maximum = ticket_fee_object.maximum_fee
        orders = Order.query.filter_by(event=event).all()
        gross_revenue = event.calc_monthly_revenue()
        invoice_amount = gross_revenue * (ticket_fee_percentage / 100)
        if invoice_amount > ticket_fee_maximum:
            invoice_amount = ticket_fee_maximum
        net_revenue = gross_revenue - invoice_amount
        payment_details = {
            'tickets_sold': event.tickets_sold,
            'gross_revenue': gross_revenue,
            'net_revenue': net_revenue,
            'amount_payable': invoice_amount,
        }
        # save invoice as pdf
        pdf = create_save_pdf(
            render_template(
                'pdf/event_invoice.html',
                orders=orders,
                user=user,
                admin_info=admin_info,
                currency=currency,
                event=event,
                ticket_fee_object=ticket_fee_object,
                payment_details=payment_details,
                net_revenue=net_revenue,
            ),
            UPLOAD_PATHS['pdf']['event_invoice'],
            dir_path='/static/uploads/pdf/event_invoices/',
            identifier=event.identifier,
        )
        # save event_invoice info to DB

        event_invoice = EventInvoice(
            amount=invoice_amount, invoice_pdf_url=pdf, event_id=event.id
        )
        save_to_db(event_invoice)


@celery.on_after_configure.connect
def setup_scheduled_task(sender, **kwargs):
    from celery.schedules import crontab

    # Every day at 5:30
    sender.add_periodic_task(crontab(hour=5, minute=30), send_after_event_mail)
    # Every 1st day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=1), send_event_fee_notification
    )
    # Every 1st day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=1), send_event_fee_notification_followup
    )
    # Every day at 5:30
    sender.add_periodic_task(
        crontab(hour=5, minute=30), change_session_state_on_event_completion
    )
    # Every 1st day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=1), send_monthly_event_invoice
    )
    # Every day at 5:00
    sender.add_periodic_task(crontab(minute=0, hour=5), event_invoices_mark_due)
    # Every 25 minutes
    sender.add_periodic_task(crontab(minute='*/25'), expire_pending_tickets)
    # Every 10 minutes
    sender.add_periodic_task(crontab(minute='*/10'), expire_initializing_tickets)
    # Every 5 minutes
    sender.add_periodic_task(crontab(minute='*/5'), delete_ticket_holders_no_order_id)

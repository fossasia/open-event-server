import datetime
import logging

import pytz
from flask_celeryext import RequestContextTask
from redis.exceptions import LockError
from sqlalchemy import and_, distinct, func, or_

from app.api.helpers.db import save_to_db
from app.api.helpers.mail import (
    send_email_after_event,
    send_email_after_event_speaker,
    send_email_ticket_sales_end,
    send_email_ticket_sales_end_next_week,
    send_email_ticket_sales_end_tomorrow,
)
from app.api.helpers.query import get_user_event_roles_by_role_name
from app.api.helpers.utilities import monthdelta
from app.instance import celery
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket import Ticket
from app.models.ticket_holder import TicketHolder
from app.settings import get_settings
from app.views.redis_store import redis_store

logger = logging.getLogger(__name__)


@celery.task(base=RequestContextTask, name='send.ticket.sales.end.mail')
def ticket_sales_end_mail():
    current_time = datetime.datetime.now()
    current_day = datetime.date.today()
    last_day = current_day - datetime.timedelta(days=1)
    next_day = current_day - datetime.timedelta(days=-1)
    next_week = current_day - datetime.timedelta(days=-7)
    events_with_expired_tickets = (
        Event.query.filter_by(state='published', deleted_at=None)
        .filter(
            Event.ends_at > current_time,
            Event.tickets.any(
                and_(
                    Ticket.deleted_at == None,
                    func.date(Ticket.sales_ends_at) == last_day,
                )
            ),
        )
        .all()
    )
    events_whose_ticket_expiring_tomorrow = (
        Event.query.filter_by(state='published', deleted_at=None)
        .filter(
            Event.ends_at > current_time,
            Event.tickets.any(
                and_(
                    Ticket.deleted_at == None,
                    func.date(Ticket.sales_ends_at) == next_day,
                )
            ),
        )
        .all()
    )
    events_whose_ticket_expiring_next_week = (
        Event.query.filter_by(state='published', deleted_at=None)
        .filter(
            Event.ends_at > current_time,
            Event.tickets.any(
                and_(
                    Ticket.deleted_at == None,
                    func.date(Ticket.sales_ends_at) == next_week,
                )
            ),
        )
        .all()
    )
    for event in events_with_expired_tickets:
        emails = get_emails_for_sales_end_email(event)
        send_email_ticket_sales_end(event, emails)

    for event in events_whose_ticket_expiring_tomorrow:
        emails = get_emails_for_sales_end_email(event)
        send_email_ticket_sales_end_tomorrow(event, emails)

    for event in events_whose_ticket_expiring_next_week:
        emails = get_emails_for_sales_end_email(event)
        send_email_ticket_sales_end_next_week(event, emails)


def get_emails_for_sales_end_email(event):
    organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
    owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
    unique_emails = set()
    for organizer in organizers:
        unique_emails.add(organizer.user.email)
    if owner:
        unique_emails.add(owner.user.email)

    emails = list(unique_emails)

    return emails


@celery.task(base=RequestContextTask, name='send.after.event.mail')
def send_after_event_mail():
    current_time = datetime.datetime.now()
    events = (
        Event.query.filter_by(state='published', deleted_at=None)
        .filter(
            Event.ends_at < current_time,
            current_time - Event.ends_at < datetime.timedelta(days=1),
        )
        .all()
    )
    for event in events:
        organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
        speakers = Speaker.query.filter_by(event_id=event.id, deleted_at=None).all()
        owner = get_user_event_roles_by_role_name(event.id, 'owner').first()
        unique_emails = set()
        unique_emails_speakers = set()
        for speaker in speakers:
            if not speaker.is_email_overridden:
                unique_emails_speakers.add(speaker.user.email)

        for organizer in organizers:
            unique_emails.add(organizer.user.email)

        if owner:
            unique_emails.add(owner.user.email)

        for email in unique_emails:
            send_email_after_event(email, event.name)

        for email in unique_emails_speakers:
            send_email_after_event_speaker(email, event.name)


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
            save_to_db(session, f'Changed {session.title} session state to rejected')


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


def this_month_date() -> datetime.datetime:
    return datetime.datetime.combine(
        datetime.date.today().replace(day=1), datetime.time()
    ).replace(tzinfo=pytz.UTC)


@celery.task(base=RequestContextTask, name='send.event.fee.notification.followup')
def send_event_fee_notification_followup(follow_up=True):
    if not follow_up:
        logger.warning('Not valid follow up request: %s', follow_up)
        return
    query = EventInvoice.query.filter(
        EventInvoice.amount > 0,
        EventInvoice.status != 'paid',
        EventInvoice.status != 'resolved',
        EventInvoice.status != 'refunded',
        EventInvoice.status != 'refunding',
    )
    this_month = this_month_date()
    if follow_up != 'post_due':
        query = query.filter(EventInvoice.issued_at >= this_month)
    else:
        # For post due invoices, we want invoices of previous month only
        # Because it gets executed on 3rd day of the next month from issued date
        last_month = monthdelta(this_month, -1)
        query = query.filter(
            EventInvoice.issued_at >= last_month, EventInvoice.issued_at < this_month
        )
    incomplete_invoices = query.all()
    logger.info(
        'Sending notification %s for %d event invoices',
        follow_up,
        len(incomplete_invoices),
    )
    for incomplete_invoice in incomplete_invoices:
        send_invoice_notification.delay(incomplete_invoice.id, follow_up=follow_up)


@celery.task(base=RequestContextTask, name='send.monthly.event.invoice')
def send_monthly_event_invoice(send_notification: bool = True):
    this_month = this_month_date()
    last_month = monthdelta(this_month, -1)
    # Find all event IDs which had a completed order last month
    last_order_event_ids = Order.query.filter(
        Order.completed_at.between(last_month, this_month)
    ).with_entities(distinct(Order.event_id))
    # SQLAlchemy returns touples instead of list of IDs
    last_order_event_ids = [r[0] for r in last_order_event_ids]
    events = (
        Event.query.filter(Event.owner != None)
        .filter(
            or_(
                Event.starts_at.between(last_month, this_month),
                Event.ends_at.between(last_month, this_month),
                Event.id.in_(last_order_event_ids),
            )
        )
        .all()
    )

    for event in events:
        send_event_invoice.delay(event.id, send_notification=send_notification)


@celery.task(base=RequestContextTask, bind=True, max_retries=5)
def send_event_invoice(
    self, event_id: int, send_notification: bool = True, force: bool = False
):
    this_month = this_month_date()
    # Check if this month's invoice has been generated
    event_invoice = (
        EventInvoice.query.filter_by(event_id=event_id)
        .filter(EventInvoice.issued_at >= this_month)
        .first()
    )
    if not force and event_invoice:
        logger.warn(
            'Event Invoice of this month for this event has already been created: %s',
            event_id,
        )
        return

    event = Event.query.get(event_id)
    try:
        # For keeping invoice numbers gapless and non-repeating, we need to generate invoices
        # one at a time. Hence, we try acquiring an expiring lock for 20 seconds, and then retry.
        # To avoid the condition of a deadlock, lock automatically expires after 5 seconds
        saved = False
        pdf_url = None
        with redis_store.lock('event_invoice_generate', timeout=5, blocking_timeout=20):
            event_invoice = EventInvoice(event=event, issued_at=this_month)
            pdf_url = event_invoice.populate()
            if pdf_url:
                try:
                    save_to_db(event_invoice)
                    saved = True
                    logger.info(
                        'Generated Event invoice %s for %s. Amount: %f',
                        event_invoice,
                        event,
                        event_invoice.amount,
                    )
                except Exception as e:
                    # For some reason, like duplicate identifier, the record might not be saved, so we
                    # retry generating the invoice and hope the error doesn't happen again
                    logger.exception('Error while saving invoice. Retrying')
                    raise self.retry(exc=e)
            else:
                logger.warning('Failed to generate event invoice PDF %s', event)
        if saved and send_notification:
            send_invoice_notification.delay(event_invoice.id)
        return pdf_url
    except LockError as e:
        logger.exception('Error while acquiring lock. Retrying')
        self.retry(exc=e)


@celery.task(base=RequestContextTask)
def send_invoice_notification(invoice_id: int, follow_up: bool = False):
    event_invoice = EventInvoice.query.get(invoice_id)
    logger.info(
        'Sending notification %s for event invoice %s of event %s',
        follow_up,
        event_invoice,
        event_invoice.event,
    )
    event_invoice.send_notification(follow_up=follow_up)


@celery.on_after_configure.connect
def setup_scheduled_task(sender, **kwargs):
    from celery.schedules import crontab

    # Every day at 5:30
    sender.add_periodic_task(crontab(hour=5, minute=30), send_after_event_mail)
    sender.add_periodic_task(crontab(hour=5, minute=30), ticket_sales_end_mail)
    # Every 1st day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=1), send_monthly_event_invoice
    )
    # Every 14th day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=14),
        send_event_fee_notification_followup.s(follow_up=True),
    )
    # Every 27th day of month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=27),
        send_event_fee_notification_followup.s(follow_up='pre_due'),
    )
    # Every 3rd day of next month at 0:00
    sender.add_periodic_task(
        crontab(minute=0, hour=0, day_of_month=3),
        send_event_fee_notification_followup.s(follow_up='post_due'),
    )
    # Every day at 5:30
    sender.add_periodic_task(
        crontab(hour=5, minute=30), change_session_state_on_event_completion
    )
    # Every 25 minutes
    sender.add_periodic_task(crontab(minute='*/25'), expire_pending_tickets)
    # Every 10 minutes
    sender.add_periodic_task(crontab(minute='*/10'), expire_initializing_tickets)
    # Every 5 minutes
    sender.add_periodic_task(crontab(minute='*/5'), delete_ticket_holders_no_order_id)

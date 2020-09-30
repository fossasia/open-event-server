import datetime
import logging

import pytz
from flask_celeryext import RequestContextTask
from redis.exceptions import LockError
from sqlalchemy import distinct, or_

from app.api.helpers.db import save_to_db
from app.api.helpers.mail import send_email_after_event
from app.api.helpers.notification import send_notif_after_event
from app.api.helpers.query import get_user_event_roles_by_role_name
from app.api.helpers.utilities import make_dict, monthdelta
from app.instance import celery
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.ticket_holder import TicketHolder
from app.settings import get_settings
from app.views.redis_store import redis_store

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
                unique_emails = set()
                user_objects = []
                for speaker in speakers:
                    if not speaker.is_email_overridden:
                        unique_emails.add(speaker.user.email)
                        user_objects.append(speaker.user)
                for organizer in organizers:
                    unique_emails.add(organizer.user.email)
                    user_objects.append(organizer.user)
                if owner:
                    unique_emails.add(owner.user.email)
                    user_objects.append(owner.user)
                for email in unique_emails:
                    send_email_after_event(email, event.name, frontend_url)
                # Unique user's dict based on their id.
                unique_users_dict = make_dict(user_objects, "id")
                for user in unique_users_dict.values():
                    send_notif_after_event(user, event.name)


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


@celery.task(base=RequestContextTask, name='send.event.fee.notification.followup')
def send_event_fee_notification_followup():
    from app.instance import current_app as app

    with app.app_context():
        incomplete_invoices = EventInvoice.query.filter(
            EventInvoice.amount > 0, EventInvoice.status != 'paid'
        ).all()
        for incomplete_invoice in incomplete_invoices:
            incomplete_invoice.send_notification(follow_up=True)


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
                except Exception as e:
                    # For some reason, like duplicate identifier, the record might not be saved, so we
                    # retry generating the invoice and hope the error doesn't happen again
                    logger.exception('Error while saving invoice. Retrying')
                    raise self.retry(exc=e)
            else:
                logger.error('Error in generating event invoice for event %s', event)
        if saved and send_notification:
            event_invoice.send_notification()
        return pdf_url
    except LockError as e:
        logger.exception('Error while acquiring lock. Retrying')
        self.retry(exc=e)


@celery.on_after_configure.connect
def setup_scheduled_task(sender, **kwargs):
    from celery.schedules import crontab

    # Every day at 5:30
    sender.add_periodic_task(crontab(hour=5, minute=30), send_after_event_mail)
    # Every 1st day of month at 0:00
    # sender.add_periodic_task(
    #     crontab(minute=0, hour=0, day_of_month=1), send_event_fee_notification_followup
    # )
    # Every 1st day of month at 0:00
    # sender.add_periodic_task(
    #     crontab(minute=0, hour=0, day_of_month=1), send_monthly_event_invoice
    # )
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

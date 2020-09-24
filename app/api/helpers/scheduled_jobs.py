import datetime
import logging

import pytz
from flask_celeryext import RequestContextTask

from app.api.helpers.db import save_to_db
from app.api.helpers.mail import send_email_after_event
from app.api.helpers.notification import send_notif_after_event
from app.api.helpers.query import get_user_event_roles_by_role_name
from app.api.helpers.utilities import make_dict
from app.instance import celery
from app.models import db
from app.models.event import Event
from app.models.event_invoice import EventInvoice
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
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


@celery.task(base=RequestContextTask, name='send.monthly.event.invoice')
def send_monthly_event_invoice():
    events = Event.query.filter_by(deleted_at=None).filter(Event.owner != None).all()

    for event in events:
        event_invoice = EventInvoice(event=event)
        pdf_url = event_invoice.populate()
        if pdf_url:
            save_to_db(event_invoice)
            event_invoice.send_notification()
        else:
            logger.error('Error in generating event invoice for event %s', event)


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

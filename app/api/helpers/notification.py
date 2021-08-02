import logging

from app.models import db
from app.models.notification import (
    Notification,
    NotificationActor,
    NotificationContent,
    NotificationType,
)
from app.models.notification_setting import NotificationSettings
from app.models.speaker import Speaker
from app.models.user import User

logger = logging.getLogger(__name__)


def send_notification(notification_content: NotificationContent, user=None, users=None):
    if not NotificationSettings.is_enabled(notification_content.type):
        logger.info(
            'Notification of type %s are disabled, hence skipping',
            notification_content.type,
        )
        return
    users = users or []
    if user:
        users.append(user)

    if not users:
        raise ValueError('Either provide user or users for sending notification')

    for user in set(users):
        notification = Notification(content=notification_content, user=user)
        db.session.add(notification)

    db.session.commit()


def notify_new_session(session):
    event = session.event
    users = event.notify_staff
    content = NotificationContent(
        type=NotificationType.NEW_SESSION,
        target=session,
        actors=[NotificationActor(actor_id=session.creator_id)],
    )

    send_notification(content, users=users)


def notify_session_state_change(session, actor):
    speakers = (
        Speaker.query.filter_by(deleted_at=None, is_email_overridden=False)
        .filter(Speaker.email != None, Speaker.sessions.contains(session))
        .with_entities(Speaker.email)
        .all()
    )
    emails = [val[0] for val in speakers]
    users = User.query.filter(User._email.in_(emails)).all()

    content = NotificationContent(
        type=NotificationType.SESSION_STATE_CHANGE,
        target=session,
        target_action=session.state,
        actors=[NotificationActor(actor=actor)],
    )

    if not users:
        logger.warning(
            'No speaker to send notification for state change of session %s', session
        )
        return

    send_notification(content, users=users)


def notify_monthly_payment(invoice, follow_up=False):
    type = (
        NotificationType.MONTHLY_PAYMENT_FOLLOWUP
        if follow_up
        else NotificationType.MONTHLY_PAYMENT
    )

    content = NotificationContent(type=type, target=invoice)

    send_notification(content, user=invoice.user)


def notify_event_role_invitation(invite, user, actor):
    content = NotificationContent(
        type=NotificationType.EVENT_ROLE,
        target=invite,
        actors=[NotificationActor(actor=actor)],
    )

    send_notification(content, user)


def notify_ticket_purchase_organizer(order):
    # TODO: Need to discuss behaviour
    return
    event = order.event
    users = event.notify_staff
    content = NotificationContent(
        type=NotificationType.TICKET_PURCHASED_ORGANIZER,
        target=order,
        actors=[NotificationActor(actor=order.user)],
    )

    send_notification(content, users=users)


def notify_ticket_purchase_attendee(order):
    buyer = order.user

    content = NotificationContent(
        type=NotificationType.TICKET_PURCHASED,
        target=order,
        actors=[NotificationActor(actor=order.user)],
    )

    send_notification(content, buyer)

    attendees = [
        attendee.user
        for attendee in order.ticket_holders
        if attendee.user and attendee.user != buyer
    ]

    if attendees:
        content = NotificationContent(
            type=NotificationType.TICKET_PURCHASED_ATTENDEE,
            target=order,
            actors=[NotificationActor(actor=order.user)],
        )

        send_notification(content, users=attendees)


def notify_ticket_cancel(order, actor):
    buyer = order.user

    content = NotificationContent(
        type=NotificationType.TICKET_CANCELLED,
        target=order,
        actors=[NotificationActor(actor=actor)],
    )

    send_notification(content, buyer)

    users = order.event.notify_staff

    content = NotificationContent(
        type=NotificationType.TICKET_CANCELLED_ORGANIZER,
        target=order,
        actors=[NotificationActor(actor=actor)],
    )

    send_notification(content, users=users)

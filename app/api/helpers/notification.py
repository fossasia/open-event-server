from flask import current_app

from app.api.helpers.db import save_to_db
from app.api.helpers.log import record_activity
from app.api.helpers.system_notifications import NOTIFS, get_event_exported_actions, get_event_imported_actions, \
    get_monthly_payment_notification_actions, get_monthly_payment_follow_up_notification_actions, \
    get_ticket_purchased_attendee_notification_actions, get_ticket_purchased_notification_actions, \
    get_ticket_purchased_organizer_notification_actions, get_new_session_notification_actions, \
    get_session_accept_reject_notification_actions, get_event_role_notification_actions
from app.models.message_setting import MessageSettings
from app.models.notification import Notification, NEW_SESSION, SESSION_ACCEPT_REJECT, \
    EVENT_IMPORTED, EVENT_IMPORT_FAIL, EVENT_EXPORTED, EVENT_EXPORT_FAIL, MONTHLY_PAYMENT_NOTIF, \
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF, EVENT_ROLE, AFTER_EVENT, TICKET_PURCHASED_ORGANIZER, \
    TICKET_PURCHASED_ATTENDEE, TICKET_PURCHASED, TICKET_CANCELLED, TICKET_CANCELLED_ORGANIZER


def send_notification(user, title, message, actions=None):
    """
    Helper function to send notifications.
    :param user:
    :param title:
    :param message:
    :param actions:
    :return:
    """
    if not current_app.config['TESTING']:
        notification = Notification(user_id=user.id,
                                    title=title,
                                    message=message
                                    )
        if not actions:
            actions = []
        notification.actions = actions
        save_to_db(notification, msg="Notification saved")
        record_activity('notification_event', user=user, title=title, actions=actions)


def send_notif_new_session_organizer(user, event_name, link, session_id):
    """
    Send notification to the event organizer about a new session.
    :param user:
    :param event_name:
    :param link:
    :param session_id:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=NEW_SESSION).first()
    if not message_settings or message_settings.notification_status == 1:
        actions = get_new_session_notification_actions(session_id, link)
        notification = NOTIFS[NEW_SESSION]
        title = notification['title'].format(event_name=event_name)
        message = notification['message'].format(event_name=event_name, link=link)

        send_notification(user, title, message, actions)


def send_notif_session_accept_reject(user, session_name, acceptance, link, session_id):
    """
    Send notification to the session creator about a session being accepted or rejected.
    :param user:
    :param session_name:
    :param acceptance:
    :param link:
    :param session_id:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.notification_status == 1:
        actions = get_session_accept_reject_notification_actions(session_id, link)
        notification = NOTIFS[SESSION_ACCEPT_REJECT]
        title = notification['title'].format(session_name=session_name,
                                             acceptance=acceptance)
        message = notification['message'].format(
            session_name=session_name,
            acceptance=acceptance
        )

        send_notification(user, title, message, actions)


def send_notif_after_import(user, event_id=None, event_name=None, event_url=None, error_text=None):
    """send notification after event import"""
    if error_text:
        send_notification(
            user=user,
            title=NOTIFS[EVENT_IMPORT_FAIL]['title'],
            message=NOTIFS[EVENT_IMPORT_FAIL]['message'].format(
                error_text=error_text)
        )
    elif event_name:
        actions = get_event_imported_actions(event_id, event_url)
        send_notification(
            user=user,
            title=NOTIFS[EVENT_IMPORTED]['title'].format(event_name=event_name),
            message=NOTIFS[EVENT_IMPORTED]['message'].format(
                event_name=event_name, event_url=event_url),
            actions=actions
        )


def send_notif_after_export(user, event_name, download_url=None, error_text=None):
    """send notification after event import"""
    if error_text:
        send_notification(
            user=user,
            title=NOTIFS[EVENT_EXPORT_FAIL]['title'].format(event_name=event_name),
            message=NOTIFS[EVENT_EXPORT_FAIL]['message'].format(
                error_text=error_text)
        )
    elif download_url:
        actions = get_event_exported_actions(download_url)
        send_notification(
            user=user,
            title=NOTIFS[EVENT_EXPORTED]['title'].format(event_name=event_name),
            message=NOTIFS[EVENT_EXPORTED]['message'].format(
                event_name=event_name, download_url=download_url),
            actions=actions
        )


def send_notif_monthly_fee_payment(user, event_name, previous_month, amount, app_name, link, event_id):
    """
    Send notification about monthly fee payments.
    :param user:
    :param event_name:
    :param previous_month:
    :param amount:
    :param app_name:
    :param link:
    :param event_id:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.notification_status == 1:
        actions = get_monthly_payment_notification_actions(event_id, link)
        notification = NOTIFS[MONTHLY_PAYMENT_NOTIF]
        title = notification['title'].format(date=previous_month,
                                             event_name=event_name)
        message = notification['message'].format(
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
        )

        send_notification(user, title, message, actions)


def send_followup_notif_monthly_fee_payment(user, event_name, previous_month, amount, app_name, link, event_id):
    """
    Send follow up notifications for monthly fee payment.
    :param user:
    :param event_name:
    :param previous_month:
    :param amount:
    :param app_name:
    :param link:
    :param event_id:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.notification_status == 1:
        actions = get_monthly_payment_follow_up_notification_actions(event_id, link)
        notification = NOTIFS[MONTHLY_PAYMENT_FOLLOWUP_NOTIF]
        title = notification['title'].format(date=previous_month,
                                             event_name=event_name)
        message = notification['message'].format(
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name
        )

        send_notification(user, title, message, actions)


def send_notif_event_role(user, role_name, event_name, link, event_id):
    """
    Send notification to a user about an event role invite.
    :param user:
    :param role_name:
    :param event_name:
    :param link:
    :param event_id:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=EVENT_ROLE).first()
    if not message_settings or message_settings.notification_status == 1:
        actions = get_event_role_notification_actions(event_id, link)
        notification = NOTIFS[EVENT_ROLE]
        title = notification['title'].format(
            role_name=role_name,
            event_name=event_name
        )
        message = notification['message'].format(
            role_name=role_name,
            event_name=event_name,
            link=link
        )

        send_notification(user, title, message, actions)


def send_notif_after_event(user, event_name):
    """
    Send notification to a user after the conclusion of an event.
    :param user:
    :param event_name:
    :return:
    """
    message_settings = MessageSettings.query.filter_by(action=AFTER_EVENT).first()
    if not message_settings or message_settings.notification_status == 1:
        notif = NOTIFS[AFTER_EVENT]
        title = notif['title'].format(
            event_name=event_name
        )
        message = notif['message'].format(
            event_name=event_name
        )

        send_notification(user, title, message)


def send_notif_ticket_purchase_organizer(user, invoice_id, order_url, event_name, subject_id):
    """Send notification with order invoice link after purchase"""
    actions = get_ticket_purchased_organizer_notification_actions(subject_id, order_url)
    send_notification(
        user=user,
        title=NOTIFS[TICKET_PURCHASED_ORGANIZER]['title'].format(
            invoice_id=invoice_id,
            event_name=event_name
        ),
        message=NOTIFS[TICKET_PURCHASED_ORGANIZER]['message'],
        actions=actions
    )


def send_notif_to_attendees(order, purchaser_id):
    """
    Send notification to attendees of an order.
    :param order:
    :param purchaser_id:
    :return:
    """
    for holder in order.ticket_holders:
        if holder.user:
            # send notification if the ticket holder is a registered user.
            if holder.user.id != purchaser_id:
                # The ticket holder is not the purchaser
                actions = get_ticket_purchased_attendee_notification_actions(holder.pdf_url)
                send_notification(
                    user=holder.user,
                    title=NOTIFS[TICKET_PURCHASED_ATTENDEE]['title'].format(
                        event_name=order.event.name
                    ),
                    message=NOTIFS[TICKET_PURCHASED_ATTENDEE]['message'],
                    actions=actions
                )
            else:
                # The Ticket purchaser
                actions = get_ticket_purchased_notification_actions(order.id, order.tickets_pdf_url)
                send_notification(
                    user=holder.user,
                    title=NOTIFS[TICKET_PURCHASED]['title'].format(
                        invoice_id=order.invoice_number
                    ),
                    message=NOTIFS[TICKET_PURCHASED]['message'],
                    actions=actions
                )


def send_notif_ticket_cancel(order):
    """Send notification with order invoice link after cancel"""
    send_notification(
        user=order.user,
        title=NOTIFS[TICKET_CANCELLED]['title'].format(
            invoice_id=order.invoice_number,
            event_name=order.event.name
        ),
        message=NOTIFS[TICKET_CANCELLED]['message'].format(
            cancel_note=order.cancel_note,
            event_name=order.event.name
        )
    )
    for organizer in order.event.organizers:
        send_notification(
            user=organizer,
            title=NOTIFS[TICKET_CANCELLED_ORGANIZER]['title'].format(
                invoice_id=order.invoice_number
            ),
            message=NOTIFS[TICKET_CANCELLED_ORGANIZER]['message'].format(
                cancel_note=order.cancel_note,
                invoice_id=order.invoice_number
            )
        )


def send_notification_with_action(user, action, **kwargs):
    """
    A general notif helper to use in auth APIs
    :param user: user to which notification is to be sent
    :param action:
    :param kwargs:
    :return:
    """

    send_notification(
        user=user,
        title=NOTIFS[action]['subject'].format(**kwargs),
        message=NOTIFS[action]['message'].format(**kwargs)
    )

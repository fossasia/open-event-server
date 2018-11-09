"""
User Notification Structures and Actions.
"""
from app.api.helpers.db import save_to_db
from app.models.notification import (
    EVENT_ROLE,
    NEW_SESSION,
    SESSION_SCHEDULE,
    NEXT_EVENT,
    SESSION_ACCEPT_REJECT,
    INVITE_PAPERS,
    AFTER_EVENT,
    EVENT_PUBLISH,
    USER_CHANGE_EMAIL,
    PASSWORD_CHANGE,
    TICKET_PURCHASED,
    TICKET_RESEND_ORGANIZER,
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    EVENT_IMPORT_FAIL,
    EVENT_IMPORTED,
    MONTHLY_PAYMENT_NOTIF,
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF,
    TICKET_PURCHASED_ORGANIZER,
    TICKET_PURCHASED_ATTENDEE,
    TICKET_CANCELLED,
    TICKET_CANCELLED_ORGANIZER,
    NotificationAction)


def get_event_exported_actions(download_url):
    """
    Get the actions associated with a notification about an event being successfully exported.
    :param download_url: download url of the event.
    :return: actions.
    """
    download_action = NotificationAction(
        subject='event-export',
        link=download_url,
        action_type='download'
    )
    save_to_db(download_action)
    return [download_action]


def get_event_imported_actions(event_id, event_url):
    """
    Get the actions associated with a notification about an event being successfully imported.
    :param event_id: id of the event.
    :param event_url: url of the event.
    :return: actions
    """
    view_event_action = NotificationAction(
        subject='event',  # subject is still 'event' since the action will be to view the imported event.
        link=event_url,
        subject_id=event_id,
        action_type='view'
    )
    save_to_db(view_event_action)
    return [view_event_action]


def get_monthly_payment_notification_actions(event_id, payment_url):
    """
    Get the actions associated with a notification of monthly payments.
    :param event_id: id of the event.
    :param payment_url: url to view invoice.
    :return: actions
    """
    view_invoice_action = NotificationAction(
        subject='event',
        link=payment_url,
        subject_id=event_id,
        action_type='view'
    )
    save_to_db(view_invoice_action)
    return [view_invoice_action]


def get_monthly_payment_follow_up_notification_actions(event_id, payment_url):
    """
    Get the actions associated with a follow up notification of monthly payments.
    :param event_id: id of the event.
    :param payment_url: url to view invoice.
    :return: actions
    """
    view_invoice_action = NotificationAction(
        subject='invoice',
        link=payment_url,
        subject_id=event_id,
        action_type='view'
    )
    save_to_db(view_invoice_action)
    return [view_invoice_action]


def get_ticket_purchased_notification_actions(order_id, order_url):
    """
    Get the actions associated with a notification of tickets purchased.
    :param order_id: order id
    :param order_url: order invoice url.
    :return:
    """
    view_order_invoice_action = NotificationAction(
        subject='order',
        link=order_url,
        subject_id=order_id,
        action_type='view'
    )
    save_to_db(view_order_invoice_action)
    return [view_order_invoice_action]


def get_ticket_purchased_attendee_notification_actions(pdf_url):
    """
    Get the actions associated with a notification of tickets purchased for an attendee that is not the buyer.
    :param pdf_url:
    :return: actions
    """
    view_ticket_action = NotificationAction(
        subject='tickets-pdf',
        link=pdf_url,
        action_type='view'
    )
    save_to_db(view_ticket_action)
    return [view_ticket_action]


def get_ticket_purchased_organizer_notification_actions(order_id, order_url):
    """
    Get the actions associated with a notification of tickets purchased for the event organizer.
    :param order_id: order id
    :param order_url: order url
    :return: actions
    """
    view_ticket_action = NotificationAction(
        subject='order',
        subject_id=order_id,
        link=order_url,
        action_type='view'
    )
    save_to_db(view_ticket_action)
    return [view_ticket_action]


def get_event_published_notification_actions(event_id, event_link):
    """
    Get the actions associated with a notification of an event getting published.
    :param event_id: event id
    :param event_link: event url
    :return: actions
    """
    view_event_action = NotificationAction(
        subject='event',
        subject_id=event_id,
        link=event_link,
        action_type='view'
    )
    save_to_db(view_event_action)
    return [view_event_action]


def get_event_role_notification_actions(event_id, invitation_link):
    """
    Get the actions associated with a notification of an event role.
    :param event_id: ID of the event.
    :param invitation_link: link for invitation.
    :return: actions
    """
    accept_event_role_action = NotificationAction(
        subject='event-role',
        subject_id=event_id,
        link=invitation_link,
        action_type='view'
    )
    save_to_db(accept_event_role_action)
    return [accept_event_role_action]


def get_new_session_notification_actions(session_id, link):
    """
    Get the actions associated with a notification of an event getting a new session proposal.
    :param session_id: id of the session.
    :param link: link to view the session.
    :return: actions
    """
    view_session_action = NotificationAction(
        subject='session',
        link=link,
        subject_id=session_id,
        action_type='view'
    )
    save_to_db(view_session_action)
    return [view_session_action]


def get_session_schedule_notification_actions(session_id, link):
    """
    Get the actions associated with a notification of change in schedule of a session.
    :param session_id: id of the session.
    :param link: link to view the session.
    :return: actions
    """
    view_session_action = NotificationAction(
        subject='session',
        link=link,
        subject_id=session_id,
        action_type='view'
    )
    save_to_db(view_session_action)
    return [view_session_action]


def get_next_event_notification_actions(event_id, link):
    """
    Get the actions associated with a notification of next event.
    :param event_id: id of the event.
    :param link: link to view the event.
    :return: actions
    """
    view_event_action = NotificationAction(
        subject='event',
        link=link,
        subject_id=event_id,
        action_type='view'
    )
    save_to_db(view_event_action)
    return [view_event_action]


def get_session_accept_reject_notification_actions(session_id, link):
    """
    Get the actions associated with a notification of a session getting accepted/rejected.
    :param session_id: id of the session.
    :param link: link to view the session.
    :return: actions
    """
    view_session_action = NotificationAction(
        subject='session',
        link=link,
        subject_id=session_id,
        action_type='view'
    )
    save_to_db(view_session_action)
    return [view_session_action]


def get_invite_papers_notification_actions(cfs_link, submit_link):
    """
    Get the actions associated with an invite to submit papers.
    :param cfs_link: link of call for speakers.
    :param submit_link: link to submit papers.
    :return:
    """
    view_cfs_action = NotificationAction(
        subject='call-for-speakers',
        link=cfs_link,
        action_type='view'
    )
    submit_paper_action = NotificationAction(
        subject='call-for-speakers',
        link=submit_link,
        action_type='submit'
    )
    save_to_db(view_cfs_action)
    save_to_db(submit_paper_action)
    return [view_cfs_action, submit_paper_action]


NOTIFS = {
    EVENT_EXPORTED: {
        'recipient': 'User',
        'title': u'Event {event_name} has been exported',
        'message': (
            u"Event <strong>{event_name}</strong> has been exported successfully."
        )
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'title': u'Export of event {event_name} failed',
        'message': (
            u"The following error occurred:<br>" +
            u"<pre>{error_text}</pre>"
        )
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'title': u'Event {event_name} has been imported',
        'message': (
            u"Event <strong>{event_name}</strong> has been imported successfully."
        )
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'title': u'Import of event failed',
        'message': (
            u"The following error occurred:<br>" +
            u"<pre>{error_text}</pre>"
        )
    },
    MONTHLY_PAYMENT_NOTIF: {
        'recipient': 'Organizer',
        'subject': u'{date} - Monthly service fee invoice for {event_name}',
        'message': (
            u"The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            u"<br/> That payment for the same has to be made in two weeks." +
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '1st day of the month'
    },
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF: {
        'recipient': 'Organizer',
        'subject': u'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            u"The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            u"<br/> That payment for the same is past the due date." +
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '15th day of the month'
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'title': u'Your order invoice and tickets ({invoice_id})',
        'message': (
            u"Your order has been processed successfully."
        )
    },
    TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'User',
        'title': u'Your ticket for {event_name}',
        'message': (
            u"Your order has been processed successfully."
        )
    },
    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Organizer',
        'title': u'New ticket purchase for {event_name} : ({invoice_id}) ',
        'message': (
            u"The order has been processed successfully."
        )
    },
    TICKET_RESEND_ORGANIZER: {
        'recipient': 'Organizer',
        'title': u'Email resent for {event_name} by {buyer_email} ({invoice_id}) ',
        'message': (
            u"Email has been sent successfully."
        )
    },
    TICKET_CANCELLED: {
        'recipient': 'User',
        'title': u'Your order for {event_name} has been cancelled ({invoice_id})',
        'message': (
            u"Your order for {event_name} has been cancelled by the organizer" +
            u"<br/>Please contact the organizer for more info" +
            u"<br/>Message from the organizer: {cancel_note}."
        )
    },
    TICKET_CANCELLED_ORGANIZER: {
        'recipient': 'User',
        'title': u'Order ({invoice_id}) has been cancelled',
        'message': (
            u"Order ({invoice_id}) has been cancelled" +
            u"<br/>Cancel Note: {cancel_note}."
        )
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'title': u'Your email has been changed',
        'message': (
            u"Your email has been changed from {email} to {new_email}.<br>Please verify your new email."
        )
    },
    PASSWORD_CHANGE: {
        'recipient': 'User',
        'subject': u'{app_name}: Password Change',
        'message': (
            u"Your password has been successfully changed."
        )
    },
    AFTER_EVENT: {
        'title': u'Event {event_name} completed',
        'message': u"The event <strong>{event_name}</strong> has been completed.<br><br>",
        'recipient': 'User',
    },
    EVENT_PUBLISH: {
        'title': u'Event {event_name} has been published',
        'message': u"The event <strong>{event_name}</strong> has been published.",
        'recipient': 'User',
    },
    EVENT_ROLE: {
        'title': u'Invitation to be {role_name} at {event_name}',
        'message': u"You've been invited to be a <strong>{role_name}</strong>" +
                   u" at <strong>{event_name}</strong>.",
        'recipient': 'User',
    },
    NEW_SESSION: {
        'title': u'New session proposal for {event_name}',
        'message': u"The event <strong>{event_name}</strong> has received" +
                   u" a new session proposal.",
        'recipient': 'Organizer',
    },
    SESSION_SCHEDULE: {
        'title': u'Schedule for Session {session_name} has been changed',
        'message': u"The schedule for session <strong>{session_name}</strong>" +
                   u" has been changed.",
        'recipient': 'Organizer, Speaker',
    },
    NEXT_EVENT: {
        'title': u'Event {event_name} is coming soon',
        'message': u"Here are upcoming events: {up_coming_events}.",
        'recipient': 'Organizer, Speaker',
    },
    SESSION_ACCEPT_REJECT: {
        'title': u'Session {session_name} has been {acceptance}',
        'message': u"The session <strong>{session_name}</strong> has been" +
                   u"<strong>{acceptance}</strong> by the Organizer.",
        'recipient': 'Speaker',
    },
    INVITE_PAPERS: {
        'title': u'Invitation to Submit Papers for {event_name}',
        'message': u"You have been invited to submit papers for <strong>{event_name}</strong>.",
        'recipient': 'Speaker',
    },
}

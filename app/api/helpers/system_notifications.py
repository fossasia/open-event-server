"""
User Notification Structures and Actions.
"""
from app.api.helpers.db import save_to_db
from app.models.notification import (
    AFTER_EVENT,
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    EVENT_IMPORT_FAIL,
    EVENT_IMPORTED,
    EVENT_PUBLISH,
    EVENT_ROLE,
    INVITE_PAPERS,
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF,
    MONTHLY_PAYMENT_NOTIF,
    NEW_SESSION,
    NEXT_EVENT,
    PASSWORD_CHANGE,
    SESSION_SCHEDULE,
    SESSION_STATE_CHANGE,
    TICKET_CANCELLED,
    TICKET_CANCELLED_ORGANIZER,
    TICKET_PURCHASED,
    TICKET_PURCHASED_ATTENDEE,
    TICKET_PURCHASED_ORGANIZER,
    TICKET_RESEND_ORGANIZER,
    USER_CHANGE_EMAIL,
    NotificationAction,
)


def get_event_exported_actions(download_url):
    """
    Get the actions associated with a notification about an event being successfully exported.
    :param download_url: download url of the event.
    :return: actions.
    """
    download_action = NotificationAction(
        subject='event-export', link=download_url, action_type='download'
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
        action_type='view',
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
        subject='invoice', link=payment_url, subject_id=event_id, action_type='view'
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
        subject='order', link=order_url, subject_id=order_id, action_type='view'
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
        subject='tickets-pdf', link=pdf_url, action_type='view'
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
        subject='order', subject_id=order_id, link=order_url, action_type='view'
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
        subject='event', subject_id=event_id, link=event_link, action_type='view'
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
        action_type='view',
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
        subject='session', link=link, subject_id=session_id, action_type='view'
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
        subject='session', link=link, subject_id=session_id, action_type='view'
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
        subject='event', link=link, subject_id=event_id, action_type='view'
    )
    save_to_db(view_event_action)
    return [view_event_action]


def get_session_state_change_notification_actions(session_id, link):
    """
    Get the actions associated with a notification of a session status being changed.
    :param session_id: id of the session.
    :param link: link to view the session.
    :return: actions
    """
    view_session_action = NotificationAction(
        subject='session', link=link, subject_id=session_id, action_type='view'
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
        subject='call-for-speakers', link=cfs_link, action_type='view'
    )
    submit_paper_action = NotificationAction(
        subject='call-for-speakers', link=submit_link, action_type='submit'
    )
    save_to_db(view_cfs_action)
    save_to_db(submit_paper_action)
    return [view_cfs_action, submit_paper_action]


NOTIFS = {
    EVENT_EXPORTED: {
        'recipient': 'User',
        'title': 'Event {event_name} has been exported',
        'message': (
            "Event <strong>{event_name}</strong> has been exported successfully."
        ),
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'title': 'Export of event {event_name} failed',
        'message': ("The following error occurred:<br>" + "<pre>{error_text}</pre>"),
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'title': 'Event {event_name} has been imported',
        'message': (
            "Event <strong>{event_name}</strong> has been imported successfully."
        ),
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'title': 'Import of event {event_name} failed',
        'message': ("The following error occurred:<br>" + "<pre>{error_text}</pre>"),
    },
    MONTHLY_PAYMENT_NOTIF: {
        'recipient': 'Owner, Organizer',
        'subject': '{date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}."
            + "<br/> That payment for the same has to be made in two weeks."
            + "<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '1st day of the month',
    },
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF: {
        'recipient': 'Owner, Organizer',
        'subject': 'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}."
            + "<br/> That payment for the same is past the due date."
            + "<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '15th day of the month',
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'title': 'Your order invoice and tickets ({invoice_id})',
        'message': ("Your order has been processed successfully."),
    },
    TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'User',
        'title': 'Your ticket for {event_name}',
        'message': ("Your order has been processed successfully."),
    },
    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Owner, Organizer',
        'title': 'New ticket purchase for {event_name} : ({invoice_id})',
        'message': ("The order has been processed successfully."),
    },
    TICKET_RESEND_ORGANIZER: {
        'recipient': 'Owner, Organizer',
        'title': 'Email resent for {event_name} by {buyer_email} ({invoice_id})',
        'message': ("Email has been sent successfully."),
    },
    TICKET_CANCELLED: {
        'recipient': 'User',
        'title': 'Your order for {event_name} has been cancelled ({invoice_id})',
        'message': (
            "Your order for <a href='{event_url}'>{event_name}</a> has been cancelled by the organizer "
            + "<br/>You can visit your cancelled ticket here : <a href='{order_url}'>{invoice_id}</a> "
            + "<br/>Please contact the organizer for more info "
            + "<br/>Message from the organizer: {cancel_note}."
        ),
    },
    TICKET_CANCELLED_ORGANIZER: {
        'recipient': 'User',
        'title': 'Order ({invoice_id}) of {event_name} has been cancelled',
        'message': (
            "Order ({invoice_id}) has been cancelled "
            + "Please visit the link to check the cancelled orders for this event:"
            + " <a href='{cancel_order_page}'>{event_name}</a> "
            + "<br/>Cancel Note: {cancel_note}."
        ),
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'title': 'Your email has been changed',
        'message': (
            "Your email has been changed from {email} to {new_email}.<br>Please verify your new email."
        ),
    },
    PASSWORD_CHANGE: {
        'recipient': 'User',
        'subject': '{app_name}: Password Change',
        'message': ("Your password has been successfully changed."),
    },
    AFTER_EVENT: {
        'title': 'Event {event_name} completed',
        'message': "The event <strong>{event_name}</strong> has been completed.<br><br>",
        'recipient': 'User',
    },
    EVENT_PUBLISH: {
        'title': 'Event {event_name} has been published',
        'message': "The event <strong>{event_name}</strong> has been published.",
        'recipient': 'User',
    },
    EVENT_ROLE: {
        'title': 'Invitation to be {role_name} at {event_name}',
        'message': "You've been invited to be one of the <strong>{role_name}s</strong>"
        + " at <strong>{event_name}</strong>.",
        'recipient': 'User',
    },
    NEW_SESSION: {
        'title': 'New session proposal for {event_name}',
        'message': "The event <strong>{event_name}</strong> has received"
        + " a new session proposal.",
        'recipient': 'Owner, Organizer',
    },
    SESSION_SCHEDULE: {
        'title': 'Schedule for Session {session_name} has been changed',
        'message': "The schedule for session <strong>{session_name}</strong>"
        + " has been changed.",
        'recipient': 'Owner, Organizer, Speaker',
    },
    NEXT_EVENT: {
        'title': 'Event {event_name} is coming soon',
        'message': "Here are upcoming events: {up_coming_events}.",
        'recipient': 'Owner, Organizer, Speaker',
    },
    SESSION_STATE_CHANGE: {
        'title': 'Session {session_name} has been {acceptance}',
        'message': "The session <strong>{session_name}</strong> has been"
        + " <strong>{acceptance}</strong> by the Organizer.",
        'recipient': 'Speaker',
    },
    INVITE_PAPERS: {
        'title': 'Invitation to Submit Papers for {event_name}',
        'message': "You have been invited to submit papers for <strong>{event_name}</strong>.",
        'recipient': 'Speaker',
    },
}

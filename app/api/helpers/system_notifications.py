"""
User Notification Structures
"""
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
    TICKET_CANCELLED_ORGANIZER
)

NOTIFS = {
    EVENT_EXPORTED: {
        'recipient': 'User',
        'title': u'Event {event_name} has been exported',
        'message': (
            u"Event <strong>{event_name}</strong> has been exported successfully." +
            u"<br><br><a href='{download_url}' class='btn btn-info btn-sm'>Download</a>"
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
            u"Event <strong>{event_name}</strong> has been imported successfully." +
            u"<br><br><a href='{event_url}' class='btn btn-info btn-sm'>View Event</a>"
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
            u"<br/> That payment for the same has to be made in two weeks. <a href='{payment_url}'>Click here</a> to " +
            u"view your invoice and complete the payment." +
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '1st day of the month'
    },
    MONTHLY_PAYMENT_FOLLOWUP_NOTIF: {
        'recipient': 'Organizer',
        'subject': u'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            u"The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            u"<br/> That payment for the same is past the due date. <a href='{payment_url}'>Click here</a> to " +
            u"view your invoice and complete the payment to prevent loss of functionality." +
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '15th day of the month'
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'title': u'Your order invoice and tickets ({invoice_id})',
        'message': (
            u"Your order has been processed successfully." +
            u"<br><br><a href='{order_url}' class='btn btn-info btn-sm'>View Invoice</a>"
        )
    },
    TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'User',
        'title': u'Your ticket for {event_name}',
        'message': (
            u"Your order has been processed successfully." +
            u"<br><br><a href='{pdf_url}' class='btn btn-info btn-sm'>View PDF</a>"
        )
    },
    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Organizer',
        'title': u'New ticket purchase for {event_name} : ({invoice_id}) ',
        'message': (
            u"The order has been processed successfully." +
            u"<br><br><a href='{order_url}' class='btn btn-info btn-sm'>View Invoice</a>"
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
        'message': u"The event <strong>{event_name}</strong> has been published.<br><br>" +
                   u"<a href='{link}' class='btn btn-info btn-sm'>View Event</a>",
        'recipient': 'User',
    },
    EVENT_ROLE: {
        'title': u'Invitation to be {role_name} at {event_name}',
        'message': u"You've been invited to be a <strong>{role_name}</strong>" +
                   u"at <strong>{event_name}</strong>.<br><br>" +
                   u"To accept the role please sign up using the following link: " +
                   u"<a href='{link}' target='_blank'>Link</a>.",
        'recipient': 'User',
    },
    NEW_SESSION: {
        'title': u'New session proposal for {event_name}',
        'message': u"The event <strong>{event_name}</strong> has received" +
                   u"a new session proposal.<br><br>" +
                   u"<a href='{link}' class='btn btn-info btn-sm'>View Session</a>",
        'recipient': 'Organizer',
    },
    SESSION_SCHEDULE: {
        'title': u'Schedule for Session {session_name} has been changed',
        'message': u"The schedule for session <strong>{session_name}</strong>" +
                   u"has been changed.<br><br>" +
                   u"<a href='{link}' class='btn btn-info btn-sm'>View Session</a>",
        'recipient': 'Organizer, Speaker',
    },
    NEXT_EVENT: {
        'title': u'Event {event_name} is coming soon',
        'message': u"Here are upcoming events: {up_coming_events}.<br><br>" +
                   u"<a href='{link}' class='btn btn-info btn-sm'>View Event</a>",
        'recipient': 'Organizer, Speaker',
    },
    SESSION_ACCEPT_REJECT: {
        'title': u'Session {session_name} has been {acceptance}',
        'message': u"The session <strong>{session_name}</strong> has been" +
                   u"<strong>{acceptance}</strong> by the Organizer.<br><br>" +
                   u"<a href='{link}' class='btn btn-info btn-sm'>View Session</a>",
        'recipient': 'Speaker',
    },
    INVITE_PAPERS: {
        'title': u'Invitation to Submit Papers for {event_name}',
        'message': u"You have been invited to submit papers for <strong>{event_name}</strong>.<br><br>" +
                   u"<a href='{cfs_link}' class='btn btn-info btn-sm'>View Call for Speakers</a>" +
                   u"<a href='{submit_link}' class='btn btn-success btn-sm'>Submit</a>",
        'recipient': 'Speaker',
    },
}

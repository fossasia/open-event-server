"""
User Notification Structures
"""
from app.models.notifications import (
    EVENT_ROLE_INVITE,
    NEW_SESSION,
    SESSION_SCHEDULE,
    NEXT_EVENT,
    SESSION_ACCEPT_REJECT,
    INVITE_PAPERS,
    AFTER_EVENT,
    EVENT_PUBLISH,
    USER_CHANGE_EMAIL,
    TICKET_PURCHASED,
    TICKET_RESEND_ORGANIZER,
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    TICKET_PURCHASED_ORGANIZER
)

NOTIFS = {
    EVENT_EXPORTED: {
        'recipient': 'User',
        'title': u'Event {event_name} has been exported',
        'message': (
            u"Event <strong>{event_name}</strong> has been exported successfully."
            u"<br><br><a href='{download_url}' class='btn btn-info btn-sm'>Download</a>"
        )
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'title': u'Export of event {event_name} failed',
        'message': (
            u"The following error occurred:<br>"
            u"<pre>{error_text}</pre>"
        )
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'title': u'Your order invoice and tickets ({invoice_id})',
        'message': (
            u"Your order has been processed successfully."
            u"<br><br><a href='{order_url}' class='btn btn-info btn-sm'>View Invoice</a>"
        )
    },
    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Organizer',
        'title': u'New ticket purchase for {event_name} by {buyer_email} ({invoice_id}) ',
        'message': (
            u"The order has been processed successfully."
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
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'title': u'Your email has been changed',
        'message': (
            u"Your email has been changed from {email} to {new_email}.<br>Please verify your new email."
        )
    },
    AFTER_EVENT: {
        'title': u'Event {event_name} completed',
        'message': u"""The event <strong>{event_name}</strong> has been completed.<br><br>""",
        'recipient': 'User',
    },
    EVENT_PUBLISH: {
        'title': u'Event {event_name} has been published',
        'message': u"""The event <strong>{event_name}</strong> has been published.<br><br>
                   <a href='{link}' class='btn btn-info btn-sm'>View Event</a>""",
        'recipient': 'User',
    },
    EVENT_ROLE_INVITE: {
        'title': u'Invitation to be {role_name} at {event_name}',
        'message': u"""You've been invited to be a <strong>{role_name}</strong>
            at <strong>{event_name}</strong>.<br><br>
            <a href='{accept_link}' class='btn btn-success btn-sm'>Accept</a>
            <a href='{decline_link}' class='btn btn-danger btn-sm'>Decline</a>""",
        'recipient': 'User',
    },
    NEW_SESSION: {
        'title': u'New session proposal for {event_name}',
        'message': u"""The event <strong>{event_name}</strong> has received
             a new session proposal.<br><br>
            <a href='{link}' class='btn btn-info btn-sm'>View Session</a>""",
        'recipient': 'Organizer',
    },
    SESSION_SCHEDULE: {
        'title': u'Schedule for Session {session_name} has been changed',
        'message': u"""The schedule for session <strong>{session_name}</strong>
             has been changed.<br><br>
            <a href='{link}' class='btn btn-info btn-sm'>View Session</a>""",
        'recipient': 'Organizer, Speaker',
    },
    NEXT_EVENT: {
        'title': u'Event {event_name} is coming soon',
        'message': u"""Here are upcoming events: {up_coming_events}.<br><br>
            <a href='{link}' class='btn btn-info btn-sm'>View Event</a>""",
        'recipient': 'Organizer, Speaker',
    },
    SESSION_ACCEPT_REJECT: {
        'title': u'Session {session_name} has been {acceptance}',
        'message': u"""The session <strong>{session_name}</strong> has been
             <strong>{acceptance}</strong> by the Organizer.<br><br>
            <a href='{link}' class='btn btn-info btn-sm'>View Session</a>""",
        'recipient': 'Speaker',
    },
    INVITE_PAPERS: {
        'title': u'Invitation to Submit Papers for {event_name}',
        'message': u"""You have been invited to submit papers for <strong>{event_name}</strong>.<br><br>
            <a href='{cfs_link}' class='btn btn-info btn-sm'>View Call for Speakers</a>
            <a href='{submit_link}' class='btn btn-success btn-sm'>Submit</a>""",
        'recipient': 'Speaker',
    },
}

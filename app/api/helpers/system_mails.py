"""
All the System mails
Register a mail here before using it
"""
from app.models.mail import (
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    EVENT_IMPORT_FAIL,
    EVENT_IMPORTED,
    EVENT_ROLE,
    MONTHLY_PAYMENT_EMAIL,
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
    MONTHLY_PAYMENT_POST_DUE_EMAIL,
    MONTHLY_PAYMENT_PRE_DUE_EMAIL,
    NEW_SESSION,
    PASSWORD_CHANGE,
    PASSWORD_RESET,
    PASSWORD_RESET_AND_VERIFY,
    SESSION_STATE_CHANGE,
    TEST_MAIL,
    TICKET_CANCELLED,
    TICKET_PURCHASED,
    TICKET_PURCHASED_ATTENDEE,
    TICKET_PURCHASED_ORGANIZER,
    USER_CHANGE_EMAIL,
    USER_CONFIRM,
    USER_REGISTER,
)

MAILS = {
    SESSION_STATE_CHANGE: {
        'recipient': 'Speaker',
        'pending': {
            'subject': 'Your speaker submission for {event_name} titled {session_name}',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "We have received your submission {session_name} for {event_name}<br/><br/>"
            "Your proposal will be reviewed by the event organizers and review team. The current status of your session is now \"Pending\".<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'accepted': {
            'subject': 'Accepted! Congratulations Your submission for {event_name} titled {session_name} has been Accepted',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Accepted\". Congratulations!<br/><br/>"
            "Your proposal will be scheduled by the event organizers and review team. Please (re)confirm your participation with the organizers of the event, if required.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'confirmed': {
            'subject': 'Confirmed! Congratulations Your submission for {event_name} titled {session_name} has been Confirmed',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Confirmed\". Congratulations!<br/><br/>"
            "Your proposal will be scheduled by the event organizers and review team. Please inform the event organizers in case there are any changes to your participation.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'rejected': {
            'subject': 'Not Accepted. Your submission for {event_name} titled {session_name} was not accepted',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Unfortunately your submission {session_name} for {event_name} was not accepted. Your session status was changed to \"Rejected\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'canceled': {
            'subject': 'Canceled! Your submission for {event_name} titled {session_name} has been Canceled',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Canceled\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
        'withdrawn': {
            'subject': 'Withdrawn! Your submission for {event_name} titled {session_name} has been Withdrawn',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "Your session status for the submission {session_name} for {event_name} was changed to \"Withdrawn\".<br/><br/>"
            "The status change was done by event organizers. If there are questions about this change please contact the organizers.<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_cfs_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
    },
    NEW_SESSION: {
        'recipient': 'Owner, Organizer',
        'subject': 'New session proposal for {session.event.name} titled {session.title}',
    },
    USER_REGISTER: {
        'recipient': 'User',
        'subject': 'Welcome to {app_name}. Please verify your account',
    },
    USER_CONFIRM: {
        'recipient': 'User',
        'subject': 'Email Confirmation to Create Account for Open-Event',
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'subject': 'Your email has been already changed',
    },
    PASSWORD_RESET: {
        'recipient': 'User',
        'subject': '{app_name}: Password Reset',
    },
    PASSWORD_RESET_AND_VERIFY: {
        'recipient': 'User',
        'subject': '{app_name}: Reset your password and verify your account',
    },
    PASSWORD_CHANGE: {
        'recipient': 'User',
        'subject': '{app_name}: Password Change',
    },
    EVENT_ROLE: {
        'recipient': 'User',
        'subject': 'Invitation to be {role} at {event}',
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'subject': 'Your order invoice and tickets for {event_name} ({invoice_id}) ',
    },
    TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'Attendee',
        'subject': 'Your tickets for {event_name} ({invoice_id}) ',
    },
    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Owner, Organizer, Coorganizer',
        'subject': 'New ticket purchase for {event_name} by {buyer_email} ({invoice_id}) ',
    },
    TICKET_CANCELLED: {
        'recipient': 'User',
        'subject': 'Your order for {event_name} has been cancelled ({invoice_id})',
    },
    EVENT_EXPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been exported',
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Export of event {event_name} failed',
    },
    MONTHLY_PAYMENT_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '1st day of the month',
    },
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '15th day of the month',
    },
    MONTHLY_PAYMENT_PRE_DUE_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'sent_at': '27th day of the month',
    },
    MONTHLY_PAYMENT_POST_DUE_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Please pay your overdue invoice for {event_name} for {date} on {app_name}',
        'sent_at': '30th day of the month',
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been imported',
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Import of event failed',
    },
    TEST_MAIL: {
        'recipient': 'User',
        'subject': 'Test Mail Subject',
        'message': ("This is a  <strong> Test </strong> E-mail."),
    },
}

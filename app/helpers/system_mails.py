"""
All the System mails
Register a mail here before using it
"""
from ..models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, \
    USER_REGISTER, PASSWORD_RESET, EVENT_ROLE, SESSION_ACCEPT_REJECT, \
    SESSION_SCHEDULE, NEXT_EVENT, EVENT_PUBLISH, AFTER_EVENT, USER_CHANGE_EMAIL, USER_REGISTER_WITH_PASSWORD, \
    TICKET_PURCHASED, EVENT_EXPORTED, EVENT_EXPORT_FAIL, MAIL_TO_EXPIRED_ORDERS, MONTHLY_PAYMENT_EMAIL, \
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL, EVENT_IMPORTED, EVENT_IMPORT_FAIL

MAILS = {
    EVENT_PUBLISH: {
        'recipient': 'Organizer, Speaker',
        'subject': '{event_name} is Live',
        'message': (
            "Hi {email}<br/>" +
            "Event, {event_name}, is up and running and ready for action. Go ahead and check it out." +
            "<br/> Visit this link to view it: {link}"
        )
    },
    INVITE_PAPERS: {
        'recipient': 'Speaker',
        'subject': 'Invitation to Submit Papers for {event_name}',
        'message': (
            "Hi {email}<br/>" +
            "You are invited to submit papers for event: {event_name}" +
            "<br/> Visit this link to fill up details: {link}"
        )
    },
    SESSION_ACCEPT_REJECT: {
        'recipient': 'Speaker',
        'subject': 'Session {session_name} has been {acceptance}',
        'message': (
            "Hi {email},<br/>" +
            "The session <strong>{session_name}</strong> has been <strong>{acceptance}</strong> by the organizer. " +
            "<br/> Visit this link to view the session: {link}"
        )
    },
    SESSION_SCHEDULE: {
        'recipient': 'Organizer, Speaker',
        'subject': 'Schedule for Session {session_name} has been changed',
        'message': (
            "Hi {email},<br/>" +
            "The schedule for session <strong>{session_name}</strong> has been changed. " +
            "<br/> Visit this link to view the session: {link}"
        )
    },
    NEXT_EVENT: {
        'recipient': 'Organizer, Speaker',
        'subject': 'Event {event_name} is coming soon',
        'message': (
            "Hi {email},<br/>" +
            "Here are the upcoming events: {up_coming_events} .Get ready!! " +
            "<br/> Visit this link to view the event: {link}"
        )
    },
    AFTER_EVENT: {
        'recipient': 'Organizer, Speaker',
        'subject': 'Event {event_name} is over',
        'message': (
            "Hi {email},<br/>" +
            "Thank You for participating in our event. We hope you enjoyed it. "
            "Please check the list of more upcoming events" +
            "Here are the upcoming events: {up_coming_events} .Get ready!! "
        ),
        'sent_at': '1 day after the event'
    },
    NEW_SESSION: {
        'recipient': 'Organizer',
        'subject': 'New session proposal for {event_name}',
        'message': (
            "Hi {email},<br/>" +
            "The event <strong>{event_name}</strong> has received a new session proposal. " +
            "<br/> Visit this link to view the session: {link}"
        )
    },
    USER_REGISTER: {
        'recipient': 'User',
        'subject': 'Account Created on Open Event',
        'message': (
            "Your Account Has Been Created! Congratulations!" +
            "<br/> Your login: {email}"
        )
    },
    USER_REGISTER_WITH_PASSWORD: {
        'recipient': 'User',
        'subject': 'Welcome to Open Event',
        'message': (
            "Your Account Has Been Created! Congratulations!" +
            "<br/> <strong>Your login:</strong><br><strong>Email:</strong> {email}<br>"
            "<strong>Password:</strong> {password}<br><br> Please login and change your password as soon as possible"
        )
    },
    USER_CONFIRM: {
        'recipient': 'User',
        'subject': 'Email Confirmation to Create Account for Open-Event',
        'message': (
            "Hi {email},<br/>" +
            "Please visit this link to confirm your email: {link}"
        )
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'subject': 'Your email has been already changed',
        'message': (
            "Hi {email},<br/>" +
            "Your email has been already changed from {email} to {new_email}. You should verify your new email"
        )
    },
    PASSWORD_RESET: {
        'recipient': 'User',
        'subject': 'Open Event: Password Reset',
        'message': (
            "Please use the following link to reset your password.<br> {link}"
        )
    },
    EVENT_ROLE: {
        'recipient': 'User',
        'subject': 'Invitation to be {role} at {event}',
        'message': (
            "Hello {email},<br><br>" +
            "You've been invited to be a <strong>{role}</strong> at <strong>{event}</strong>.<br>" +
            "To accept the role please sign up using the following link: <a href='{link}' target='_blank'>Link</a>."
        )
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'subject': 'Your order invoice and tickets ({invoice_id})',
        'message': (
            "Your order has been processed successfully." +
            "<br/> <a href='{order_url}'>Click here</a> to view/download your invoice."
            "<br><br><em>Looking forward to seeing you at the event.</em>"
        )
    },
    EVENT_EXPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been exported',
        'message': (
            "Click on the following link to download the event." +
            "<br> <a href='{download_url}'>Download</a>"
        )
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Export of event {event_name} failed',
        'message': (
            "The error was as follows - <br>" +
            "<pre>{error_text}</pre>"
        )
    },
    MAIL_TO_EXPIRED_ORDERS: {
        'recipient': 'User',
        'subject': 'Tickets for {event_name} are still available ',
        'message': (
            "This is just a gentle reminder that the payment for your order {invoice_id} is still left." +
            "<br/> The tickets for this event are still available. <a href='{order_url}'>Click here</a> to "
            "purchase your ticket for this event."
            "<br><br><em>Looking forward to seeing you at the event.</em>"
        )
    },
    MONTHLY_PAYMENT_EMAIL: {
        'recipient': 'Organizer',
        'subject': '{date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            "<br/> That payment for the same has to be made in two weeks. <a href='{payment_url}'>Click here</a> to "
            "view your invoice and complete the payment."
            "<br><br><em>Thank you for using Open Event.</em>"
        ),
        'sent_at': '1st day of the month'
    },
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL: {
        'recipient': 'Organizer',
        'subject': 'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            "<br/> That payment for the same is past the due date. <a href='{payment_url}'>Click here</a> to "
            "view your invoice and complete the payment to prevent loss of functionality."
            "<br><br><em>Thank you for using Open Event.</em>"
        ),
        'sent_at': '15th day of the month'
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'subject': u'Event {event_name} has been imported',
        'message': (
            "Click on the following link to manage your event" +
            "<br> <a href='{event_url}'>Link</a>"
        )
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Import of event failed',
        'message': (
            "The error was as follows - <br>" +
            "<pre>{error_text}</pre>"
        )
    }
}

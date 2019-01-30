"""
All the System mails
Register a mail here before using it
"""
from app.models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, \
    USER_REGISTER, PASSWORD_RESET, EVENT_ROLE, SESSION_ACCEPT_REJECT, \
    SESSION_SCHEDULE, NEXT_EVENT, EVENT_PUBLISH, AFTER_EVENT, USER_CHANGE_EMAIL, USER_REGISTER_WITH_PASSWORD, \
    TICKET_PURCHASED, EVENT_EXPORTED, EVENT_EXPORT_FAIL, MAIL_TO_EXPIRED_ORDERS, MONTHLY_PAYMENT_EMAIL, \
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL, EVENT_IMPORTED, EVENT_IMPORT_FAIL, TICKET_PURCHASED_ORGANIZER, TICKET_CANCELLED, \
    TICKET_PURCHASED_ATTENDEE, PASSWORD_CHANGE, PASSWORD_RESET_AND_VERIFY

MAILS = {
    EVENT_PUBLISH: {
        'recipient': 'Organizer, Speaker',
        'subject': u'{event_name} is Live',
        'message': (
            u"Hi {email}<br/>" +
            u"Event, {event_name}, is up and running and ready for action. Go ahead and check it out." +
            u"<br/> Visit this link to view it: {link}"
        )
    },
    INVITE_PAPERS: {
        'recipient': 'Speaker',
        'subject': u'Invitation to Submit Papers for {event_name}',
        'message': (
            u"Hi {email}<br/>" +
            u"You are invited to submit papers for event: {event_name}" +
            u"<br/> Visit this link to fill up details: {link}"
        )
    },
    SESSION_ACCEPT_REJECT: {
        'recipient': 'Speaker',
        'subject': u'Session {session_name} has been {acceptance}',
        'message': (
            u"Hi {email},<br/>" +
            u"The session <strong>{session_name}</strong> has been <strong>{acceptance}</strong> by the organizer. " +
            u"<br/> Visit this link to view the session: {link}"
        )
    },
    SESSION_SCHEDULE: {
        'recipient': 'Organizer, Speaker',
        'subject': u'Schedule for Session {session_name} has been changed',
        'message': (
            u"Hi {email},<br/>" +
            u"The schedule for session <strong>{session_name}</strong> has been changed. " +
            u"<br/> Visit this link to view the session: {link}"
        )
    },
    NEXT_EVENT: {
        'recipient': 'Organizer, Speaker',
        'subject': u'Event {event_name} is coming soon',
        'message': (
            u"Hi {email},<br/>" +
            u"Here are the upcoming events: {up_coming_events} .Get ready!! " +
            u"<br/> Visit this link to view the event: {link}"
        )
    },
    AFTER_EVENT: {
        'recipient': 'Organizer, Speaker',
        'subject': u'Event {event_name} is over',
        'message': (
            u"Hi {email},<br/>" +
            u"Thank You for participating in our event. We hope you enjoyed it. "
            u"Please check the list of more upcoming events" +
            u"Here are the upcoming events: {upcoming_events} .Get ready!! "
        ),
        'sent_at': '1 day after the event'
    },
    NEW_SESSION: {
        'recipient': 'Organizer',
        'subject': u'New session proposal for {event_name}',
        'message': (
            u"Hi {email},<br/>" +
            u"The event <strong>{event_name}</strong> has received a new session proposal. " +
            u"<br/> Visit this link to view the session: {link}"
        )
    },
    USER_REGISTER: {
        'recipient': 'User',
        'subject': u'Account Created on {app_name}',
        'message': (
            u"Your Account Has Been Created! Congratulations!" +
            u"<br/> Your login: {email}"
        )
    },
    USER_REGISTER_WITH_PASSWORD: {
        'recipient': 'User',
        'subject': u'Welcome to {app_name}',
        'message': (
            u"Your Account Has Been Created! Congratulations!" +
            u"<br/> <strong>Your login:</strong><br><strong>Email:</strong> {email}<br>"
        )
    },
    USER_CONFIRM: {
        'recipient': 'User',
        'subject': u'Email Confirmation to Create Account for Open-Event',
        'message': (
            u"Hi {email},<br/>" +
            u"Please visit this link to confirm your email: {link}"
        )
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'subject': u'Your email has been already changed',
        'message': (
            u"Hi {email},<br/>" +
            u"Your email has been already changed from {email} to {new_email}. You should verify your new email"
        )
    },
    PASSWORD_RESET: {
        'recipient': 'User',
        'subject': u'{app_name}: Password Reset',
        'message': (
            u"Please use the following link to reset your password.<br> <a href='{link}' target='_blank'>{link}</a>"
        )
    },
    PASSWORD_RESET_AND_VERIFY: {
        'recipient': 'User',
        'subject': u'{app_name}: Reset your password and verify your account',
        'message': (
            u"Please use the following link to reset your password and verify your account." +
            "<br> <a href='{link}' target='_blank'>{link}</a>"
        )

    },
    PASSWORD_CHANGE: {
        'recipient': 'User',
        'subject': u'{app_name}: Password Change',
        'message': (
            u"Your password has been successfully changed. Please login with your new password."
        )
    },
    EVENT_ROLE: {
        'recipient': 'User',
        'subject': u'Invitation to be {role} at {event}',
        'message': (
            u"Hello {email},<br><br>" +
            u"You've been invited to be a <strong>{role}</strong> at <strong>{event}</strong>.<br>" +
            u"To accept the role please sign up using the following link: <a href='{link}' target='_blank'>Link</a>."
        )
    },
    TICKET_PURCHASED: {
        'recipient': 'User',
        'subject': u'Your order invoice and tickets for {event_name} ({invoice_id}) ',
        'message': (
            u"Hi, this is a confirmation mail of your tickets for the event {event_name}"
            u"<br/>Your order has been processed successfully." +
            u"<br/> <a href='{pdf_url}'>Click here</a> to view/download your invoice."
            u"<br><br><em>Looking forward to seeing you at the event."
            u"<br/>Login to manage your orders at https://eventyay.com </em>"
        )
    },
    TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'Attendee',
        'subject': u'Your tickets for {event_name} ({invoice_id}) ',
        'message': (
            u"Hi, this is a confirmation mail of your tickets for the event {event_name}"
            u"<br/>Your order has been processed successfully." +
            u"<br/> <a href='{pdf_url}'>Click here</a> to view/download your ticket."
            u"<br><br><em>Looking forward to seeing you at the event."
        )
    },

    TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Organizer, Coorganizer',
        'subject': u'New ticket purchase for {event_name} by {buyer_email} ({invoice_id}) ',
        'message': (
            u"Hi, {buyer_email} just bought tickets for the event {event_name}"
            u"<br/>The order has been processed successfully." +
            u"<br/> <a href='{order_url}'>Click here</a> to view/download the invoice."
            u"<br/>Login to manage the orders at https://eventyay.com </em>"
        )
    },
    TICKET_CANCELLED: {
        'recipient': 'User',
        'subject': u'Your order for {event_name} has been cancelled ({invoice_id})',
        'message': (
            u"Hi,Your order for {event_name} has been cancelled has been cancelled by the organizer"
            u"<br/>Please contact the organizer for more info" +
            u"<br/>Message from the organizer: {cancel_note}"
            u"<br/> <a href='{order_url}'>Click here</a> to view/download the invoice."
            u"<br/>Login to manage the orders at https://eventyay.com </em>"
        )
    },
    EVENT_EXPORTED: {
        'recipient': 'User',
        'subject': u'Event {event_name} has been exported',
        'message': (
            u"Click on the following link to download the event." +
            u"<br> <a href='{download_url}'>Download</a>"
        )
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'subject': u'Export of event {event_name} failed',
        'message': (
            u"The error was as follows - <br>" +
            u"<pre>{error_text}</pre>"
        )
    },
    MAIL_TO_EXPIRED_ORDERS: {
        'recipient': 'User',
        'subject': u'Tickets for {event_name} are still available ',
        'message': (
            u"This is just a gentle reminder that the payment for your order {invoice_id} is still left." +
            u"<br/> The tickets for this event are still available. <a href='{order_url}'>Click here</a> to "
            u"purchase your ticket for this event."
            u"<br><br><em>Looking forward to seeing you at the event.</em>"
        )
    },
    MONTHLY_PAYMENT_EMAIL: {
        'recipient': 'Organizer',
        'subject': u'{date} - Monthly service fee invoice for {event_name}',
        'message': (
            u"The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            u"<br/> That payment for the same has to be made in two weeks. <a href='{payment_url}'>Click here</a> to "
            u"view your invoice and complete the payment."
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '1st day of the month'
    },
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL: {
        'recipient': 'Organizer',
        'subject': u'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            u"The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}." +
            u"<br/> That payment for the same is past the due date. <a href='{payment_url}'>Click here</a> to "
            u"view your invoice and complete the payment to prevent loss of functionality."
            u"<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '15th day of the month'
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'subject': u'Event {event_name} has been imported',
        'message': (
            u"Click on the following link to manage your event" +
            u"<br> <a href='{event_url}'>Link</a>"
        )
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'subject': u'Import of event failed',
        'message': (
            u"The error was as follows - <br>" +
            u"<pre>{error_text}</pre>"
        )
    }
}

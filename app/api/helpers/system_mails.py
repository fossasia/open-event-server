"""
All the System mails
Register a mail here before using it
"""
from app.models.mail import (
    AFTER_EVENT,
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    EVENT_IMPORT_FAIL,
    EVENT_IMPORTED,
    EVENT_PUBLISH,
    EVENT_ROLE,
    INVITE_PAPERS,
    MAIL_TO_EXPIRED_ORDERS,
    MONTHLY_PAYMENT_EMAIL,
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
    MONTHLY_PAYMENT_POST_DUE_EMAIL,
    MONTHLY_PAYMENT_PRE_DUE_EMAIL,
    NEW_SESSION,
    NEXT_EVENT,
    PASSWORD_CHANGE,
    PASSWORD_RESET,
    PASSWORD_RESET_AND_VERIFY,
    SESSION_SCHEDULE,
    SESSION_STATE_CHANGE,
    TEST_MAIL,
    TICKET_CANCELLED,
    TICKET_PURCHASED,
    TICKET_PURCHASED_ATTENDEE,
    TICKET_PURCHASED_ORGANIZER,
    USER_CHANGE_EMAIL,
    USER_CONFIRM,
    USER_EVENT_ROLE,
    USER_REGISTER,
    USER_REGISTER_WITH_PASSWORD,
)

MAILS = {
    EVENT_PUBLISH: {
        'recipient': 'Owner, Organizer, Speaker',
        'subject': '{event_name} is Live',
        'message': (
            "Hi {email}<br/>"
            + "Event, {event_name}, is up and running and ready for action. Go ahead and check it out."
            + "<br/> Visit this link to view it: {link}"
        ),
    },
    INVITE_PAPERS: {
        'recipient': 'Speaker',
        'subject': 'Invitation to Submit Papers for {event_name}',
        'message': (
            "Hi {email}<br/>"
            + "You are invited to submit papers for event: {event_name}"
            + "<br/> Visit this link to fill up details: {link}"
        ),
    },
    SESSION_STATE_CHANGE: {
        'recipient': 'Speaker',
        'pending': {
            'subject': 'Your speaker submission for {event_name} titled {session_name}',
            'message': "Hello,<br/><br/>"
            "This is an automatic message from {app_name}.<br/><br/>"
            "We have received your submission {session_name} for {event_name}<br/><br/>"
            "Your proposal will be reviewed by the event organizers and review team. The current status of your session is now \"Pending\".<br/><br/>"
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
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
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
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
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
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
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
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
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
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
            "You can also check the status and details of your submission on the session page {session_link}. You need to be logged in to view it.<br/><br/>"
            "More details about the event are on the event page at {event_link}.<br/><br/>"
            "Thank you.<br/>"
            "{frontend_link}",
        },
    },
    SESSION_SCHEDULE: {
        'recipient': 'Owner, Organizer, Speaker',
        'subject': 'Schedule for Session {session_name} has been changed',
        'message': (
            "Hi {email},<br/>"
            + "The schedule for session <strong>{session_name}</strong> has been changed. "
            + "<br/> Visit this link to view the session: {link}"
        ),
    },
    NEXT_EVENT: {
        'recipient': 'Owner, Organizer, Speaker',
        'subject': 'Event {event_name} is coming soon',
        'message': (
            "Hi {email},<br/>"
            + "Here are the upcoming events: {up_coming_events} .Get ready!! "
            + "<br/> Visit this link to view the event: {link}"
        ),
    },
    AFTER_EVENT: {
        'recipient': 'Owner, Organizer, Speaker',
        'subject': 'Event {event_name} is over',
        'message': (
            "Hi {email},<br/>"
            + "Thank You for participating in our event. We hope you enjoyed it. "
            "Please check out other upcoming events around you on {url} <br />"
        ),
        'sent_at': '1 day after the event',
    },
    NEW_SESSION: {
        'recipient': 'Owner, Organizer',
        'subject': 'New session proposal for {event_name}',
        'message': (
            "Hi {email},<br/>"
            + "The event <strong>{event_name}</strong> has received a new session proposal. "
            + "<br/> Visit this link to view the session: <a href='{link}' target='_blank'>{link}</a>"
        ),
    },
    USER_REGISTER: {
        'recipient': 'User',
        'subject': 'Welcome to {app_name}. Please verify your account',
    },
    USER_REGISTER_WITH_PASSWORD: {
        'recipient': 'User',
        'subject': 'Welcome to {app_name}',
        'message': (
            "Your Account Has Been Created! Congratulations!"
            + "<br/> <strong>Your login:</strong><br><strong>Email:</strong> {email}<br>"
        ),
    },
    USER_CONFIRM: {
        'recipient': 'User',
        'subject': 'Email Confirmation to Create Account for Open-Event',
        'message': (
            "Hi {email},<br/>"
            + "Please visit this link to confirm your email:  <a href='{link}' target='_blank'>{link}</a>"
        ),
    },
    USER_CHANGE_EMAIL: {
        'recipient': 'User',
        'subject': 'Your email has been already changed',
        'message': (
            "Hi {email},<br/>"
            + "Your email has been already changed from {email} to {new_email}. You should verify your new email"
        ),
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
        'message': (
            "Hello {email},<br><br>"
            + "You've been invited to be a <strong>{role}</strong> at <strong>{event}</strong>.<br>"
            + "To accept the role please sign up using the following link: <a href='{link}' target='_blank'>Link</a>."
        ),
    },
    USER_EVENT_ROLE: {
        'recipient': 'User',
        'subject': 'Invitation to be {role} at {event}',
        'message': (
            "Hello {email},<br><br>"
            + "You've been invited to be a <strong>{role}</strong> at <strong>{event}</strong>.<br>"
            + "To accept the role please go to the following link: <a href='{link}' target='_blank'>Link</a>."
        ),
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
        'message': (
            "Hi, {buyer_email} just bought tickets for the event {event_name}"
            "<br/>The order has been processed successfully."
            "<br/> <a href='{order_url}'>Click here</a> to view/download the invoice."
            "<br/>Login to manage the orders at {frontend_url}"
        ),
    },
    TICKET_CANCELLED: {
        'recipient': 'User',
        'subject': 'Your order for {event_name} has been cancelled ({invoice_id})',
        'message': (
            "Hello,"
            "<br/>your order for {event_name} has been cancelled by the organizer."
            "<br/>Please contact the organizer for more info." + "{cancel_msg}"
            "<br/>To manage orders please login to <a href='{frontend_url}' target='_blank'>{frontend_url}</a>"
            "and visit \"My Tickets\"."
            "<br/>Best regards,"
            "<br/>{app_name} Team"
        ),
    },
    EVENT_EXPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been exported',
        'message': (
            "Click on the following link to download the event."
            + "<br> <a href='{download_url}'>Download</a>"
        ),
    },
    EVENT_EXPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Export of event {event_name} failed',
        'message': ("The error was as follows - <br>" + "<pre>{error_text}</pre>"),
    },
    MAIL_TO_EXPIRED_ORDERS: {
        'recipient': 'User',
        'subject': 'Tickets for {event_name} are still available ',
        'message': (
            "This is just a gentle reminder that the payment for your order {invoice_id} is still left."
            + "<br/> The tickets for this event are still available. <a href='{order_url}'>Click here</a> to "
            "purchase your ticket for this event."
            "<br><br><em>Looking forward to seeing you at the event.</em>"
        ),
    },
    MONTHLY_PAYMENT_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Your invoice for {event_name} for {date} is available on {app_name}',
        'message': (
            "Hello {name},<br><br>"
            "The invoice for your event {event_name} on eventyay.com for {date} is now available. Your invoice payment is due within 30 days.<br><br>"
            "Amount Due: {amount}<br><br>"
            "Please pay within 30 days.<br><br>"
            "Pay Now at: <a href='{payment_url}'>{payment_url}</a><br><br>"
            "A detailed invoice is available in <a href='https://eventyay.com/account/billing/invoices/'>the billing area</a> of your account. If you have any questions about invoices, please find more information on our FAQ at https://support.eventyay.com.<br><br>"
            "<em>Thank you for using {app_name}!</em><br><br>"
            "{app_name} Team"
        ),
        'sent_at': '1st day of the month',
    },
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'message': (
            "Hello {name},<br><br>"
            "Just a friendly reminder that we haven't received your payment for your invoice for {event_name} for {date}. Payment is fast and simple using your credit card or PayPal account.<br><br>"
            "Amount Due: {amount}<br><br>"
            "Please pay within 15 days.<br><br>"
            "Pay Now at: <a href='{payment_url}'>{payment_url}</a><br><br>"
            "A detailed invoice is available in <a href='https://eventyay.com/account/billing/invoices/'>the billing area</a> of your account. If you have any questions about invoices, please find more information on our FAQ at https://support.eventyay.com.<br><br>"
            "<em>Thank you for using {app_name}!</em><br><br>"
            "{app_name} Team"
        ),
        'sent_at': '15th day of the month',
    },
    MONTHLY_PAYMENT_PRE_DUE_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Reminder: Your invoice for {event_name} for {date} is available on {app_name}',
        'message': (
            "Hello {name},<br><br>"
            "This is a reminder that we haven't received your payment for your invoice for {event_name} for {date}. Payment is fast and simple using your credit card or PayPal account.<br><br>"
            "Amount Due: {amount}<br><br>"
            "Please pay within 2 days.<br><br>"
            "Pay Now: <a href='{payment_url}'>{payment_url}</a><br><br>"
            "Late payments can be subject to a 5% finance fee.<br><br>"
            "A detailed invoice is available in <a href='https://eventyay.com/account/billing/invoices/'>the billing area</a> of your account. If you have any questions about invoices, please find more information on our FAQ at https://support.eventyay.com.<br><br>"
            "<em>Thank you for using {app_name}!</em><br><br>"
            "{app_name} Team"
        ),
        'sent_at': '27th day of the month',
    },
    MONTHLY_PAYMENT_POST_DUE_EMAIL: {
        'recipient': 'Owner',
        'subject': 'Please pay your overdue invoice for {event_name} for {date} on {app_name}',
        'message': (
            "Hello {name},<br><br>"
            "Your payment is now past due.<br>Please pay this invoice immediately to avoid your account being suspended.<br><br>"
            "Amount Due: {amount}<br><br>"
            "Please pay immediately at: <a href='{payment_url}'>{payment_url}</a><br><br>"
            "Late payments can be subject to a 5% finance fee.<br><br>"
            "A detailed invoice is available in <a href='https://eventyay.com/account/billing/invoices/'>the billing area</a> of your account. If you have any questions about invoices, please find more information on our FAQ at https://support.eventyay.com.<br><br>"
            "If you feel this invoice is incorrect or have any questions, you can contact our support team for assistance.<br><br>"
            "<em>Thank you for using {app_name}!</em><br><br>"
            "{app_name} Team"
        ),
        'sent_at': '30th day of the month',
    },
    EVENT_IMPORTED: {
        'recipient': 'User',
        'subject': 'Event {event_name} has been imported',
        'message': (
            "Click on the following link to manage your event"
            + "<br> <a href='{event_url}'>Link</a>"
        ),
    },
    EVENT_IMPORT_FAIL: {
        'recipient': 'User',
        'subject': 'Import of event failed',
        'message': ("The error was as follows - <br>" + "<pre>{error_text}</pre>"),
    },
    TEST_MAIL: {
        'recipient': 'User',
        'subject': 'Test Mail Subject',
        'message': ("This is a  <strong> Test </strong> E-mail."),
    },
}

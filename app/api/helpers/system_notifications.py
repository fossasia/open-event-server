"""
User Notification Structures and Actions.
"""
from app.models.notification import NotificationType

NOTIFS = {
    NotificationType.MONTHLY_PAYMENT: {
        'recipient': 'Owner, Organizer',
        'subject': '{date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}."
            + "<br/> That payment for the same has to be made in two weeks."
            + "<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '1st day of the month',
    },
    NotificationType.MONTHLY_PAYMENT_FOLLOWUP: {
        'recipient': 'Owner, Organizer',
        'subject': 'Past Due: {date} - Monthly service fee invoice for {event_name}',
        'message': (
            "The total service fee for the ticket sales of {event_name} in the month of {date} is {amount}."
            + "<br/> That payment for the same is past the due date."
            + "<br><br><em>Thank you for using {app_name}.</em>"
        ),
        'sent_at': '15th day of the month',
    },
    NotificationType.TICKET_PURCHASED: {
        'recipient': 'User',
        'title': 'Your order invoice and tickets ({invoice_id})',
        'message': ("Your order has been processed successfully."),
    },
    NotificationType.TICKET_PURCHASED_ATTENDEE: {
        'recipient': 'User',
        'title': 'Your ticket for {event_name}',
        'message': ("Your order has been processed successfully."),
    },
    NotificationType.TICKET_PURCHASED_ORGANIZER: {
        'recipient': 'Owner, Organizer',
        'title': 'New ticket purchase for {event_name} : ({invoice_id})',
        'message': ("The order has been processed successfully."),
    },
    NotificationType.TICKET_CANCELLED: {
        'recipient': 'User',
        'title': 'Your order for {event_name} has been cancelled ({invoice_id})',
        'message': (
            "Your order for <a href='{event_url}'>{event_name}</a> has been cancelled by the organizer "
            + "<br/>You can visit your cancelled ticket here : <a href='{order_url}'>{invoice_id}</a> "
            + "<br/>Please contact the organizer for more info "
            + "<br/>Message from the organizer: {cancel_note}."
        ),
    },
    NotificationType.TICKET_CANCELLED_ORGANIZER: {
        'recipient': 'User',
        'title': 'Order ({invoice_id}) of {event_name} has been cancelled',
        'message': (
            "Order ({invoice_id}) has been cancelled "
            + "Please visit the link to check the cancelled orders for this event:"
            + " <a href='{cancel_order_page}'>{event_name}</a> "
            + "<br/>Cancel Note: {cancel_note}."
        ),
    },
    NotificationType.EVENT_ROLE: {
        'title': 'Invitation to be {role_name} at {event_name}',
        'message': "You've been invited to be one of the <strong>{role_name}s</strong>"
        + " at <strong>{event_name}</strong>.",
        'recipient': 'User',
    },
    NotificationType.NEW_SESSION: {
        'title': 'New session proposal for {event_name}',
        'message': "The event <strong>{event_name}</strong> has received"
        + " a new session proposal.",
        'recipient': 'Owner, Organizer',
    },
    NotificationType.SESSION_STATE_CHANGE: {
        'title': 'Session {session_name} has been {acceptance}',
        'message': "The session <strong>{session_name}</strong> has been"
        + " <strong>{acceptance}</strong> by the Organizer.",
        'recipient': 'Speaker',
    },
}

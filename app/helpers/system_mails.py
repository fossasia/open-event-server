"""
All the System mails
Register a mail here before using it
"""
from ..models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, \
    USER_REGISTER, PASSWORD_RESET, EVENT_ROLE, SESSION_ACCEPT_REJECT, \
    SESSION_SCHEDULE, NEXT_EVENT, EVENT_PUBLISH, AFTER_EVENT, USER_CHANGE_EMAIL, USER_REGISTER_WITH_PASSWORD

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
            "Thank You for participating in our event. We hope you enjoyed it. Please check the list of more upcoming events" +
            "Here are the upcoming events: {up_coming_events} .Get ready!! "
        )
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
            "Your email has been already changed from {email} to {new_email}. You should verified your new email"
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
    }
}

"""
All the System mails
Register a mail here before using it
"""
from ..models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, \
    USER_REGISTER, PASSWORD_RESET, EVENT_ROLE, SESSION_ACCEPT_REJECT, \
    SESSION_SCHEDULE


MAILS = {
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
            "The session <strong>{session_name}</strong> has been <strong>{acceptance}</strong> by the organizer. "
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
    USER_CONFIRM: {
        'recipient': 'User',
        'subject': 'Email Confirmation to Create Account for Open-Event',
        'message': (
            "Hi {email},<br/>" +
            "Please visit this link to confirm your email: {link}"
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
            "Hello {email},<br>" +
            "You've been invited to be a {role} at {event}. " +
            "Please follow the link to accept the role: {link}"
        )
    }
}

"""
User Notification Structures
"""
from open_event.models.notifications import (
    EVENT_ROLE_INVITE,
    NEW_SESSION,
    SESSION_SCHEDULE,
    NEXT_EVENT,
    SESSION_ACCEPT_REJECT,
    INVITE_PAPERS,
)

NOTIFS = {
    EVENT_ROLE_INVITE: {
        'title': 'Invitation to be {role} at {event}',
        'message': ("You've been invited to be a <strong>{role}</strong>"
            " at <strong>{event}</strong>.<br>Please follow the link to"
            " accept the role: <a href='{link}'>Link</a>."),
        'recipient': 'User',
    },
    NEW_SESSION: {
        'title': 'New session proposal for {event_name}',
        'message': ("The event <strong>{event_name}</strong> has received"
            " a new session proposal.<br/>Please visit this link to view"
            " the session: {link}."),
        'recipient': 'Organizer',
    },
    SESSION_SCHEDULE: {
        'title': 'Schedule for Session {session_name} has been changed',
        'message': ("The schedule for session <strong>{session_name}</strong>"
            " has been changed.<br/> Please visit this link to view the"
            " session: {link}."),
        'recipient': 'Organizer, Speaker',
    },
    NEXT_EVENT: {
        'title': 'Event {event_name} is coming soon',
        'message': ("Here are the upcoming events: {up_coming_events}."
            "<br/>Please visit this link to view the event: {link}."),
        'recipient': 'Organizer, Speaker',
    },
    SESSION_ACCEPT_REJECT: {
        'title': 'Session {session_name} has been {acceptance}',
        'message': ("The session <strong>{session_name}</strong> has been"
            " <strong>{acceptance}</strong> by the Organizer.<br/> Please"
            " visit this link to view the session: {link}."),
        'recipient': 'Speaker',
    },
    INVITE_PAPERS: {
        'title': 'Invitation to Submit Papers for {event_name}',
        'message': ("You have been invited to submit papers for {event_name}."
            "<br/> Please visit this link to fill up details: {link}."),
        'recipient': 'Speaker',
    },
}

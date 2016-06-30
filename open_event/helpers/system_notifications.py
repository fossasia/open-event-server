"""
User Notification Structures
"""
from open_event.models.notifications import EVENT_ROLE_INVITE

NOTIFS = {
    EVENT_ROLE_INVITE : {
        'title': 'Invitation to be {role} at {event}',
        'message': ("You've been invited to be a <strong>{role}</strong>"
            " at <strong>{event}</strong>.<br>Please follow the link to"
            " accept the role: <a href='{link}'>Link</a>."),
        'recipient': 'User',
    },
}

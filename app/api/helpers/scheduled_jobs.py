from app.models.event import Event
from app.api.helpers.query import get_upcoming_events, get_user_event_roles_by_role_name
from app.api.helpers.mail import send_email_after_event
from app.settings import get_settings

import datetime
import pytz


def send_after_event_mail():
    from app import current_app as app
    with app.app_context():
        events = Event.query.all()
        upcoming_events = get_upcoming_events()
        upcoming_event_links = "<ul>"
        for upcoming_event in upcoming_events:
            frontend_url = get_settings()['frontend_url']
            upcoming_event_links += "<li><a href='{}/events/{}'>{}</a></li>" \
                .format(frontend_url, upcoming_event.id, upcoming_event.name)
        upcoming_event_links += "</ul>"
        for event in events:
            organizers = get_user_event_roles_by_role_name(event.id, 'organizer')
            speakers = get_user_event_roles_by_role_name(event.id, 'speaker')
            current_time = datetime.datetime.now(pytz.timezone(event.timezone))
            time_difference = current_time - event.ends_at
            time_difference_minutes = (time_difference.days * 24 * 60) + (time_difference.seconds / 60)
            if current_time > event.ends_at and time_difference_minutes < 1440:
                for speaker in speakers:
                    send_email_after_event(speaker.user.email, event.id, upcoming_event_links)
                for organizer in organizers:
                    send_email_after_event(organizer.user.email, event.id, upcoming_event_links)

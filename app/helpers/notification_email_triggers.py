from flask import url_for
from app.helpers.data_getter import DataGetter
from app.helpers.helpers import send_new_session_organizer, send_notif_new_session_organizer, \
    send_notif_session_accept_reject, send_session_accept_reject, send_schedule_change, send_notif_session_schedule


def trigger_new_session_notifications(session_id, event_id=None, event=None):

    if not event and not event_id:
        raise Exception('event or event_id is required')
    if not event:
        event = DataGetter.get_event(event_id)

    link = url_for('event_sessions.session_display_view',
                   event_id=event.id, session_id=session_id, _external=True)

    organizers = DataGetter.get_user_event_roles_by_role_name(event_id, 'organizer')
    for organizer in organizers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(organizer.user.id, event_id)
        if email_notification_setting and email_notification_setting.new_paper == 1:
            send_new_session_organizer(organizer.user.email, event.name, link)
        # Send notification
        send_notif_new_session_organizer(organizer.user, event.name, link)

def trigger_session_state_change_notifications(session, event_id, state=None):
    if not state:
        state = session.state
    link = url_for('event_sessions.session_display_view', event_id=event_id, session_id=session.id, _external=True)
    for speaker in session.speakers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(speaker.user_id, event_id)
        if email_notification_setting and email_notification_setting.session_accept_reject == 1:
            send_session_accept_reject(speaker.email, session.title, state, link)
            # Send notification
            send_notif_session_accept_reject(speaker.user, session.title, state, link)

def trigger_session_schedule_change_notifications(session, event_id):
    link = url_for('event_sessions.session_display_view', event_id=event_id, session_id=session.id, _external=True)
    for speaker in session.speakers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(speaker.user_id, event_id)
        if email_notification_setting and email_notification_setting.session_schedule == 1:
            send_schedule_change(speaker.email, session.title, link)
            # Send notification
            send_notif_session_schedule(speaker.user, session.title, link)

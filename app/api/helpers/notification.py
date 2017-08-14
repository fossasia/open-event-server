from flask import current_app

from app.api.helpers.db import save_to_db
from app.models.notification import Notification, NEW_SESSION, SESSION_ACCEPT_REJECT
from app.models.message_setting import MessageSettings
from app.api.helpers.log import record_activity
from app.api.helpers.system_notifications import NOTIFS


def send_notification(user, action, title, message):
    if not current_app.config['TESTING']:
        notification = Notification(user_id=user.id,
                                    title=title,
                                    message=message,
                                    action=action
                                    )
        save_to_db(notification, msg="Notification saved")
        record_activity('notification_event', user=user, action=action, title=title)


def send_notif_new_session_organizer(user, event_name, link):
    message_settings = MessageSettings.query.filter_by(action=NEW_SESSION).first()
    if not message_settings or message_settings.notification_status == 1:
        notif = NOTIFS[NEW_SESSION]
        action = NEW_SESSION
        title = notif['title'].format(event_name=event_name)
        message = notif['message'].format(event_name=event_name, link=link)

        send_notification(user, action, title, message)


def send_notif_session_accept_reject(user, session_name, acceptance, link):
    message_settings = MessageSettings.query.filter_by(action=SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.notification_status == 1:
        notif = NOTIFS[SESSION_ACCEPT_REJECT]
        action = SESSION_ACCEPT_REJECT
        title = notif['title'].format(session_name=session_name,
                                      acceptance=acceptance)
        message = notif['message'].format(
            session_name=session_name,
            acceptance=acceptance,
            link=link
        )

        send_notification(user, action, title, message)

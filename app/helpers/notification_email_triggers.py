from flask import url_for

from app.helpers.data_getter import DataGetter
from app.helpers.helpers import send_new_session_organizer, send_notif_new_session_organizer, \
    send_notif_session_accept_reject, send_session_accept_reject, send_schedule_change, send_notif_session_schedule, \
    send_email_for_after_purchase_organizers, send_notif_for_after_purchase_organizer, send_notif_for_resend
from app.models.mail import NEW_SESSION, SESSION_ACCEPT_REJECT, SESSION_SCHEDULE, TICKET_PURCHASED


def trigger_new_session_notifications(session_id, event_id=None, event=None):
    if not event and not event_id:
        raise Exception('event or event_id is required')
    if not event:
        event = DataGetter.get_event(event_id)

    link = url_for('event_sessions.session_display_view',
                   event_id=event.id, session_id=session_id, _external=True)

    admin_msg_setting = DataGetter.get_message_setting_by_action(NEW_SESSION)
    organizers = DataGetter.get_user_event_roles_by_role_name(event.id, 'organizer')
    for organizer in organizers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(organizer.user.id, event.id)
        if not admin_msg_setting or \
            (email_notification_setting and email_notification_setting.new_paper == 1 and
             admin_msg_setting.user_control_status == 1) or admin_msg_setting.user_control_status == 0:

            send_new_session_organizer(organizer.user.email, event.name, link)
        # Send notification
        send_notif_new_session_organizer(organizer.user, event.name, link)


def trigger_session_state_change_notifications(session, event_id, state=None, message=None, subject=None):
    if not state:
        state = session.state
    link = url_for('event_sessions.session_display_view', event_id=event_id, session_id=session.id, _external=True)
    admin_msg_setting = DataGetter.get_message_setting_by_action(SESSION_ACCEPT_REJECT)
    for speaker in session.speakers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(speaker.user_id, event_id)
        if not admin_msg_setting or \
            (email_notification_setting and email_notification_setting.session_accept_reject == 1 and
             admin_msg_setting.user_control_status == 1) or admin_msg_setting.user_control_status == 0:

            if speaker.email:
                send_session_accept_reject(speaker.email, session.title, state, link, subject=subject, message=message)
            # Send notification
        if speaker.user:
            send_notif_session_accept_reject(speaker.user, session.title, state, link)
    session.state_email_sent = True
    from app.helpers.data import save_to_db
    save_to_db(session)


def trigger_session_schedule_change_notifications(session, event_id):
    link = url_for('event_sessions.session_display_view', event_id=event_id, session_id=session.id, _external=True)
    admin_msg_setting = DataGetter.get_message_setting_by_action(SESSION_SCHEDULE)
    for speaker in session.speakers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(speaker.user_id, event_id)
        if not admin_msg_setting or \
            (email_notification_setting and email_notification_setting.session_schedule == 1 and
             admin_msg_setting.user_control_status == 1) or admin_msg_setting.user_control_status == 0:
            if speaker.email:
                send_schedule_change(speaker.email, session.title, link)
        # Send notification
        if speaker.user:
            send_notif_session_schedule(speaker.user, session.title, link)


def trigger_after_purchase_notifications(buyer_email, event_id, event, invoice_id, order_url, resend=False):
    if not event and not event_id:
        raise Exception('event or event_id is required')
    if not event:
        event = DataGetter.get_event(event_id)

    admin_msg_setting = DataGetter.get_message_setting_by_action(TICKET_PURCHASED)
    organizers = DataGetter.get_user_event_roles_by_role_name(event.id, 'organizer')
    for organizer in organizers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(organizer.user.id, event_id)
        if not admin_msg_setting or \
            (email_notification_setting and email_notification_setting.after_ticket_purchase == 1 and
             admin_msg_setting.user_control_status == 1) or admin_msg_setting.user_control_status == 0:
            send_email_for_after_purchase_organizers(organizer.user.email, buyer_email, invoice_id, order_url, event.name, event.organizer_name)
        if resend:
            send_notif_for_resend(organizer.user, invoice_id, order_url, event.name, buyer_email)
        else:
            send_notif_for_after_purchase_organizer(organizer.user, invoice_id, order_url, event.name, buyer_email)

    coorganizers = DataGetter.get_user_event_roles_by_role_name(event.id, 'coorganizer')
    for coorganizer in coorganizers:
        email_notification_setting = DataGetter.get_email_notification_settings_by_event_id(coorganizer.user.id, event_id)
        if not admin_msg_setting or \
            (email_notification_setting and email_notification_setting.after_ticket_purchase == 1 and
                     admin_msg_setting.user_control_status == 1) or admin_msg_setting.user_control_status == 0:
            send_email_for_after_purchase_organizers(coorganizer.user.email, buyer_email, invoice_id, order_url, event.name, event.organizer_name)
        if not resend:
            send_notif_for_resend(organizer.user, invoice_id, order_url, event.name, buyer_email)
        else:
            send_notif_for_after_purchase_organizer(organizer.user, invoice_id, order_url, event.name, buyer_email)


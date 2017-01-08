import json
import os
import os.path
import re
import time
from datetime import datetime, timedelta

import requests
from flask import request, url_for, current_app
from itsdangerous import Serializer
from sqlalchemy import func

from app.helpers.flask_helpers import get_real_ip
from app.helpers.storage import UploadedFile
from app.models.notifications import (
    # Prepended with `NOTIF_` to differentiate from mails
    EVENT_ROLE_INVITE as NOTIF_EVENT_ROLE,
    NEW_SESSION as NOTIF_NEW_SESSION,
    SESSION_SCHEDULE as NOTIF_SESSION_SCHEDULE,
    NEXT_EVENT as NOTIF_NEXT_EVENT,
    SESSION_ACCEPT_REJECT as NOTIF_SESSION_ACCEPT_REJECT,
    INVITE_PAPERS as NOTIF_INVITE_PAPERS,
    USER_CHANGE_EMAIL as NOTIF_USER_CHANGE_EMAIL,
    TICKET_PURCHASED as NOTIF_TICKET_PURCHASED,
    EVENT_EXPORT_FAIL as NOTIF_EVENT_EXPORT_FAIL,
    EVENT_EXPORTED as NOTIF_EVENT_EXPORTED,

)
from app.settings import get_settings
from system_mails import MAILS
from system_notifications import NOTIFS
from ..models.mail import INVITE_PAPERS, NEW_SESSION, USER_CONFIRM, NEXT_EVENT, \
    USER_REGISTER, PASSWORD_RESET, SESSION_ACCEPT_REJECT, SESSION_SCHEDULE, EVENT_ROLE, EVENT_PUBLISH, Mail, \
    AFTER_EVENT, USER_CHANGE_EMAIL, USER_REGISTER_WITH_PASSWORD, TICKET_PURCHASED, EVENT_EXPORTED, \
    EVENT_EXPORT_FAIL, MAIL_TO_EXPIRED_ORDERS, MONTHLY_PAYMENT_FOLLOWUP_EMAIL, MONTHLY_PAYMENT_EMAIL, \
    EVENT_IMPORTED, EVENT_IMPORT_FAIL
from ..models.message_settings import MessageSettings
from ..models.track import Track


def represents_int(string):
    try:
        int(string)
        return True
    except:
        return False


# From http://stackoverflow.com/a/3425124
def monthdelta(date, delta):
    m, y = (date.month + delta) % 12, date.year + (date.month + delta - 1) // 12
    if not m:
        m = 12
    d = min(date.day, [31,
                       29 if y % 4 == 0 and not y % 400 == 0 else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31][m - 1])
    return date.replace(day=d, month=m, year=y)


def get_count(q):
    count_q = q.statement.with_only_columns([func.count()]).order_by(None)
    count = q.session.execute(count_q).scalar()
    return count


def get_event_id():
    """Get event Id from request url"""
    url = request.url
    result = re.search('event/[0-9]*', url)
    return result.group(0).split('/')[1]


#########
# Mails #
#########

def send_email_invitation(email, event_name, link):
    """Send email for submit papers"""
    message_settings = MessageSettings.query.filter_by(action=INVITE_PAPERS).first()
    if not message_settings or message_settings.mail_status == 1:
        send_email(
            to=email,
            action=INVITE_PAPERS,
            subject=MAILS[INVITE_PAPERS]['subject'].format(event_name=event_name),
            html=MAILS[INVITE_PAPERS]['message'].format(
                email=str(email),
                event_name=str(event_name),
                link=link
            )
        )


def send_new_session_organizer(email, event_name, link):
    """Send email after new sessions proposal"""
    message_settings = MessageSettings.query.filter_by(action=NEW_SESSION).first()
    if not message_settings or message_settings.mail_status == 1:
        send_email(
            to=email,
            action=NEW_SESSION,
            subject=MAILS[NEW_SESSION]['subject'].format(event_name=event_name),
            html=MAILS[NEW_SESSION]['message'].format(
                email=str(email),
                event_name=str(event_name),
                link=link
            )
        )


def send_session_accept_reject(email, session_name, acceptance, link):
    """Send session accepted or rejected"""
    message_settings = MessageSettings.query.filter_by(action=SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.mail_status == 1:
        send_email(
            to=email,
            action=SESSION_ACCEPT_REJECT,
            subject=MAILS[SESSION_ACCEPT_REJECT]['subject'].format(session_name=session_name, acceptance=acceptance),
            html=MAILS[SESSION_ACCEPT_REJECT]['message'].format(
                email=str(email),
                session_name=str(session_name),
                acceptance=str(acceptance),
                link=link
            )
        )


def send_schedule_change(email, session_name, link):
    """Send schedule change in session"""
    message_settings = MessageSettings.query.filter_by(action=SESSION_SCHEDULE).first()
    if not message_settings or message_settings.mail_status == 1:
        send_email(
            to=email,
            action=SESSION_SCHEDULE,
            subject=MAILS[SESSION_SCHEDULE]['subject'].format(session_name=session_name),
            html=MAILS[SESSION_SCHEDULE]['message'].format(
                email=str(email),
                session_name=str(session_name),
                link=link
            )
        )


def send_next_event(email, event_name, link, up_coming_events):
    """Send next event"""
    message_settings = MessageSettings.query.filter_by(action=NEXT_EVENT).first()
    if not message_settings or message_settings.mail_status == 1:
        upcoming_event_html = "<ul>"
        for event in up_coming_events:
            upcoming_event_html += "<a href='%s'><li> %s </li></a>" % (url_for('events.details_view',
                                                                               event_id=event.id, _external=True),
                                                                       event.name)
        upcoming_event_html += "</ul><br/>"
        send_email(
            to=email,
            action=NEXT_EVENT,
            subject=MAILS[NEXT_EVENT]['subject'].format(event_name=event_name),
            html=MAILS[NEXT_EVENT]['message'].format(
                email=str(email),
                event_name=str(event_name),
                link=link,
                up_coming_events=upcoming_event_html
            )
        )


def send_after_event(email, event_name, upcoming_events):
    """Send after event mail"""
    message_settings = MessageSettings.query.filter_by(action=AFTER_EVENT).first()
    if not message_settings or message_settings.mail_status == 1:
        upcoming_event_html = "<ul>"
        for event in upcoming_events:
            upcoming_event_html += "<a href='%s'><li> %s </li></a>" % (url_for('events.details_view',
                                                                               event_id=event.id, _external=True),
                                                                       event.name)
        upcoming_event_html += "</ul><br/>"
        send_email(
            to=email,
            action=AFTER_EVENT,
            subject=MAILS[AFTER_EVENT]['subject'].format(event_name=event_name),
            html=MAILS[AFTER_EVENT]['message'].format(
                email=str(email),
                event_name=str(event_name),
                up_coming_events=upcoming_event_html
            )
        )


def send_event_publish(email, event_name, link):
    """Send email on publishing event"""
    message_settings = MessageSettings.query.filter_by(action=NEXT_EVENT).first()
    if not message_settings or message_settings.mail_status == 1:
        send_email(
            to=email,
            action=NEXT_EVENT,
            subject=MAILS[EVENT_PUBLISH]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_PUBLISH]['message'].format(
                email=str(email),
                event_name=str(event_name),
                link=link
            )
        )


def send_email_after_account_create(form):
    """Send email after account create"""
    send_email(
        to=form['email'],
        action=USER_REGISTER,
        subject=MAILS[USER_REGISTER]['subject'].format(app_name=get_settings()['app_name']),
        html=MAILS[USER_REGISTER]['message'].format(email=form['email'])
    )


def send_email_after_account_create_with_password(form):
    """Send email after account create"""
    send_email(
        to=form['email'],
        action=USER_REGISTER_WITH_PASSWORD,
        subject=MAILS[USER_REGISTER_WITH_PASSWORD]['subject'].format(app_name=get_settings()['app_name']),
        html=MAILS[USER_REGISTER_WITH_PASSWORD]['message'].format(email=form['email'], password=form['password'])
    )


def send_email_confirmation(form, link):
    """account confirmation"""
    send_email(
        to=form['email'],
        action=USER_CONFIRM,
        subject=MAILS[USER_CONFIRM]['subject'],
        html=MAILS[USER_CONFIRM]['message'].format(
            email=form['email'], link=link
        )
    )


def send_email_when_changes_email(old_email, new_email):
    """account confirmation"""
    send_email(
        to=old_email,
        action=USER_CHANGE_EMAIL,
        subject=MAILS[USER_CHANGE_EMAIL]['subject'],
        html=MAILS[USER_CHANGE_EMAIL]['message'].format(
            email=old_email, new_email=new_email
        )
    )


def send_email_with_reset_password_hash(email, link):
    """Send email with reset password hash"""
    send_email(
        to=email,
        action=PASSWORD_RESET,
        subject=MAILS[PASSWORD_RESET]['subject'].format(app_name=get_settings()['app_name']),
        html=MAILS[PASSWORD_RESET]['message'].format(link=link)
    )


def send_email_for_event_role_invite(email, role, event, link):
    """
    Send Email to users for Event Role invites.
    """
    message_settings = MessageSettings.query.filter_by(action=EVENT_ROLE).first()
    if not message_settings or message_settings.mail_status == 1:
        subject = MAILS[EVENT_ROLE]['subject'].format(role=role, event=event)
        message = MAILS[EVENT_ROLE]['message'].format(
            email=email,
            role=role,
            event=event,
            link=link
        )
        send_email(
            to=email,
            action=EVENT_ROLE,
            subject=subject,
            html=message
        )


def send_email_for_after_purchase(email, invoice_id, order_url):
    """Send email with order invoice link after purchase"""
    send_email(
        to=email,
        action=TICKET_PURCHASED,
        subject=MAILS[TICKET_PURCHASED]['subject'].format(invoice_id=invoice_id),
        html=MAILS[TICKET_PURCHASED]['message'].format(order_url=order_url)
    )


def send_email_for_expired_orders(email, event_name, invoice_id, order_url):
    """Send email with order invoice link after purchase"""
    send_email(
        to=email,
        action=MAIL_TO_EXPIRED_ORDERS,
        subject=MAILS[MAIL_TO_EXPIRED_ORDERS]['subject'].format(event_name=event_name),
        html=MAILS[MAIL_TO_EXPIRED_ORDERS]['message'].format(invoice_id=invoice_id, order_url=order_url)
    )


def send_email_for_monthly_fee_payment(email, event_name, date, amount, payment_url):
    """Send email every month with invoice to pay service fee"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_EMAIL]['subject'].format(event_name=event_name, date=date),
        html=MAILS[MONTHLY_PAYMENT_EMAIL]['message'].format(event_name=event_name, date=date,
                                                            payment_url=payment_url, amount=amount,
                                                            app_name=get_settings()['app_name'])
    )


def send_followup_email_for_monthly_fee_payment(email, event_name, date, amount, payment_url):
    """Send email every month with invoice to pay service fee"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['subject'].format(event_name=event_name, date=date),
        html=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['message'].format(event_name=event_name, date=date,
                                                                     payment_url=payment_url, amount=amount,
                                                                     app_name=get_settings()['app_name'])
    )


def send_email_after_export(email, event_name, result):
    """send email after event export"""
    if '__error' in result:
        send_email(
            email,
            action=EVENT_EXPORT_FAIL,
            subject=MAILS[EVENT_EXPORT_FAIL]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_EXPORT_FAIL]['message'].format(error_text=result['result']['message'])
        )
    else:
        send_email(
            email,
            action=EVENT_EXPORTED,
            subject=MAILS[EVENT_EXPORTED]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_EXPORTED]['message'].format(
                download_url=request.url_root.strip('/') + result['download_url']
            )
        )


def send_email_after_import(email, result):
    """send email after event import"""
    if '__error' in result:
        send_email(
            email,
            action=EVENT_IMPORT_FAIL,
            subject=MAILS[EVENT_IMPORT_FAIL]['subject'],
            html=MAILS[EVENT_IMPORT_FAIL]['message'].format(error_text=result['result']['message'])
        )
    else:
        send_email(
            email,
            action=EVENT_IMPORTED,
            subject=MAILS[EVENT_IMPORTED]['subject'].format(event_name=result['name']),
            html=MAILS[EVENT_IMPORTED]['message'].format(
                event_url=request.url_root.strip('/') + '/events/%d' % result['id']
            )
        )


def send_email(to, action, subject, html):
    """
    Sends email and records it in DB
    """
    if not string_empty(to):
        email_service = get_settings()['email_service']
        email_from = get_settings()['email_from']
        payload = {
            'to': to,
            'from': email_from,
            'subject': subject,
            'html': html
        }

        if not current_app.config['TESTING']:
            if email_service == 'smtp':
                smtp_encryption = get_settings()['smtp_encryption']
                if smtp_encryption == 'tls':
                    smtp_encryption = 'required'
                elif smtp_encryption == 'ssl':
                    smtp_encryption = 'ssl'
                elif smtp_encryption == 'tls_optional':
                    smtp_encryption = 'optional'
                else:
                    smtp_encryption = 'none'

                config = {
                    'host': get_settings()['smtp_host'],
                    'username': get_settings()['smtp_username'],
                    'password': get_settings()['smtp_password'],
                    'encryption': smtp_encryption,
                    'port': get_settings()['smtp_port'],
                }

                from tasks import send_mail_via_smtp_task
                send_mail_via_smtp_task.delay(config, payload)
            else:
                key = get_settings()['sendgrid_key']
                if not key and not current_app.config['TESTING']:
                    print 'Sendgrid key not defined'
                    return
                headers = {
                    "Authorization": ("Bearer " + key)
                }
                from tasks import send_email_task
                send_email_task.delay(payload, headers)

        # record_mail(to, action, subject, html)
        mail = Mail(
            recipient=to, action=action, subject=subject,
            message=html, time=datetime.now()
        )

        from data import save_to_db, record_activity
        save_to_db(mail, 'Mail Recorded')
        record_activity('mail_event', email=to, action=action, subject=subject)
    return


#################
# Notifications #
#################


def send_notification(user, action, title, message):
    # DataManager imported here to prevent circular dependency
    from app.helpers.data import DataManager
    DataManager.create_user_notification(user, action, title, message)


def send_notif_after_export(user, event_name, result):
    """send notification after event export"""
    if '__error' in result:
        send_notification(
            user=user,
            action=NOTIF_EVENT_EXPORT_FAIL,
            title=NOTIFS[NOTIF_EVENT_EXPORT_FAIL]['title'].format(event_name=event_name),
            message=NOTIFS[NOTIF_EVENT_EXPORT_FAIL]['message'].format(error_text=result['result']['message'])
        )
    else:
        send_notification(
            user=user,
            action=NOTIF_EVENT_EXPORTED,
            title=NOTIFS[NOTIF_EVENT_EXPORTED]['title'].format(event_name=event_name),
            message=NOTIFS[NOTIF_EVENT_EXPORTED]['message'].format(
                event_name=event_name, download_url=result['download_url'])
        )


def send_notif_for_after_purchase(user, invoice_id, order_url):
    """Send notification with order invoice link after purchase"""
    send_notification(
        user=user,
        action=NOTIF_TICKET_PURCHASED,
        title=NOTIFS[NOTIF_TICKET_PURCHASED]['title'].format(invoice_id=invoice_id),
        message=NOTIFS[NOTIF_TICKET_PURCHASED]['message'].format(order_url=order_url)
    )


def send_notif_when_changes_email(user, old_email, new_email):
    send_notification(
        user=user,
        action=NOTIF_USER_CHANGE_EMAIL,
        title=NOTIFS[NOTIF_USER_CHANGE_EMAIL]['title'],
        message=NOTIFS[NOTIF_USER_CHANGE_EMAIL]['message'].format(
            email=old_email, new_email=new_email
        )
    )


def send_notif_event_role(user, role_name, event_name, accept_link, decline_link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_EVENT_ROLE).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_EVENT_ROLE]
        action = NOTIF_EVENT_ROLE
        title = notif['title'].format(
            role_name=role_name,
            event_name=event_name
        )
        message = notif['message'].format(
            role_name=role_name,
            event_name=event_name,
            accept_link=accept_link,
            decline_link=decline_link
        )

        send_notification(user, action, title, message)


def send_notif_new_session_organizer(user, event_name, link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_NEW_SESSION).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_NEW_SESSION]
        action = NOTIF_NEW_SESSION
        title = notif['title'].format(event_name=event_name)
        message = notif['message'].format(event_name=event_name, link=link)

        send_notification(user, action, title, message)


def send_notif_session_schedule(user, session_name, link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_SESSION_SCHEDULE).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_SESSION_SCHEDULE]
        action = NOTIF_SESSION_SCHEDULE
        title = notif['title'].format(session_name=session_name)
        message = notif['message'].format(session_name=session_name, link=link)

        send_notification(user, action, title, message)


def send_notif_next_event(user, event_name, up_coming_events, link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_NEXT_EVENT).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_NEXT_EVENT]
        action = NOTIF_NEXT_EVENT
        title = notif['title'].format(event_name=event_name)
        message = notif['message'].format(up_coming_events=up_coming_events,
                                          link=link)

        send_notification(user, action, title, message)


def send_notif_session_accept_reject(user, session_name, acceptance, link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_SESSION_ACCEPT_REJECT).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_SESSION_ACCEPT_REJECT]
        action = NOTIF_SESSION_ACCEPT_REJECT
        title = notif['title'].format(session_name=session_name,
                                      acceptance=acceptance)
        message = notif['message'].format(
            session_name=session_name,
            acceptance=acceptance,
            link=link
        )

        send_notification(user, action, title, message)


def send_notif_invite_papers(user, event_name, cfs_link, submit_link):
    message_settings = MessageSettings.query.filter_by(action=NOTIF_INVITE_PAPERS).first()
    if not message_settings or message_settings.notif_status == 1:
        notif = NOTIFS[NOTIF_INVITE_PAPERS]
        action = NOTIF_INVITE_PAPERS
        title = notif['title'].format(event_name=event_name)
        message = notif['message'].format(
            event_name=event_name,
            cfs_link=cfs_link,
            submit_link=submit_link
        )

        send_notification(user, action, title, message)


def ensure_social_link(website, link):
    """
    converts usernames of social profiles to full profile links
    if link is username, prepend website to it else return the link
    """
    if link == '' or link is None:
        return link
    if link.find('/') != -1:  # has backslash, so not a username
        return link
    else:
        return website + '/' + link


def get_serializer(secret_key='secret_key'):
    return Serializer(secret_key)


def get_commit_info(commit_number):
    response = requests.get("https://api.github.com/repos/fossasia/open-event-orga-server/commits/" + commit_number)
    return json.loads(response.text)


def string_empty(string):
    if type(string) is not str and type(string) is not unicode:
        return False
    if string and string.strip() and string != u'' and string != u' ':
        return False
    else:
        return True


def string_not_empty(string):
    return not string_empty(string)


def fields_not_empty(obj, fields):
    for field in fields:
        if string_empty(getattr(obj, field)):
            return False
    return True


def get_request_stats():
    """
    Get IP, Browser, Platform, Version etc
    http://werkzeug.pocoo.org/docs/0.11/utils/#module-werkzeug.useragents

    Note: request.remote_addr gives the server's address if the server is behind a reverse proxy. -@niranjan94
    """
    return {
        'ip': get_real_ip(),
        'platform': request.user_agent.platform,
        'browser': request.user_agent.browser,
        'version': request.user_agent.version,
        'language': request.user_agent.language
    }


def get_date_range(day_filter):
    day_filter = day_filter.lower()  # Use lower case for match
    format = "%Y-%m-%dT%H:%M:%S"
    date_now = datetime.now()
    start, end = None, None
    if day_filter == 'all days':
        pass
    elif day_filter == 'today':
        start = date_now.replace(hour=00, minute=00)
        end = date_now.replace(hour=23, minute=59)
    elif day_filter == 'tomorrow':
        date_now += timedelta(days=1)
        start = date_now.replace(hour=00, minute=00)
        end = date_now.replace(hour=23, minute=59)
    elif day_filter == 'this week':
        weekday = date_now.weekday()
        date_now -= timedelta(days=weekday)
        start = date_now.replace(hour=00, minute=00)
        date_now += timedelta(days=6)
        end = date_now.replace(hour=23, minute=59)
    elif day_filter == 'this weekend':
        weekday = date_now.weekday()
        date_now += timedelta(days=5 - weekday)
        start = date_now.replace(hour=00, minute=00)
        date_now += timedelta(days=1)
        end = date_now.replace(hour=23, minute=59)
    elif day_filter == 'next week':
        weekday = date_now.weekday()
        date_now -= timedelta(days=weekday)
        start = date_now.replace(hour=00, minute=00)
        date_now += timedelta(days=6)
        end = date_now.replace(hour=23, minute=59)
    elif day_filter == 'this month':
        start = first_day_of_month(date_now.replace(hour=00, minute=00))
        end = last_day_of_month(date_now.replace(hour=23, minute=59))
    else:
        try:
            from_string, to_string = day_filter.split(" to ")
            start = datetime.strptime(from_string, '%m-%d-%Y').replace(hour=00, minute=00)
            end = datetime.strptime(to_string, '%m-%d-%Y').replace(hour=23, minute=59)
        except:
            start = date_now.replace(hour=00, minute=00)
            end = date_now.replace(hour=23, minute=59)
            pass
    return start.strftime(format), end.strftime(format)


def last_day_of_month(date):
    if date.month == 12:
        return date.replace(day=31)
    return date.replace(month=date.month + 1, day=1) - timedelta(days=1)


def first_day_of_month(date):
    ddays = int(date.strftime("%d")) - 1
    delta = timedelta(days=ddays)
    return date - delta


def update_state(task_handle, state, result=None):
    """
    Update state of celery task
    """
    if result is None:
        result = {}
    if not current_app.config.get('CELERY_ALWAYS_EAGER'):
        task_handle.update_state(
            state=state, meta=result
        )


def uploaded_file(extension='.png', file_content=None):
    filename = str(time.time()) + extension
    file_path = current_app.config.get('BASE_DIR') + '/static/uploads/' + filename
    file = open(file_path, "wb")
    file.write(file_content.split(",")[1].decode('base64'))
    file.close()
    return UploadedFile(file_path, filename)

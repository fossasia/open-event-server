import base64
import logging
from datetime import datetime

from flask import current_app

from app.api.helpers.db import save_to_db
from app.api.helpers.files import make_frontend_url
from app.api.helpers.log import record_activity
from app.api.helpers.system_mails import MAILS
from app.api.helpers.utilities import get_serializer, str_generator, string_empty
from app.models.mail import (
    AFTER_EVENT,
    EVENT_EXPORT_FAIL,
    EVENT_EXPORTED,
    EVENT_IMPORT_FAIL,
    EVENT_IMPORTED,
    EVENT_ROLE,
    MONTHLY_PAYMENT_EMAIL,
    MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
    NEW_SESSION,
    SESSION_ACCEPT_REJECT,
    TEST_MAIL,
    TICKET_CANCELLED,
    TICKET_PURCHASED,
    TICKET_PURCHASED_ATTENDEE,
    USER_CHANGE_EMAIL,
    USER_CONFIRM,
    USER_EVENT_ROLE,
    Mail,
)
from app.models.user import User
from app.settings import get_settings


def check_smtp_config(smtp_encryption):
    """
    Checks config of SMTP
    """
    config = {
        'host': get_settings()['smtp_host'],
        'username': get_settings()['smtp_username'],
        'password': get_settings()['smtp_password'],
        'encryption': smtp_encryption,
        'port': get_settings()['smtp_port'],
    }
    for field in config:
        if field is None:
            return False
    return True


def send_email(to, action, subject, html, attachments=None):
    """
    Sends email and records it in DB
    """
    from .tasks import send_email_task_sendgrid, send_email_task_smtp

    if not string_empty(to):
        email_service = get_settings()['email_service']
        email_from_name = get_settings()['email_from_name']
        if email_service == 'smtp':
            email_from = email_from_name + '<' + get_settings()['email_from'] + '>'
        else:
            email_from = get_settings()['email_from']
        payload = {
            'to': to,
            'from': email_from,
            'subject': subject,
            'html': html,
            'attachments': attachments,
        }

        if not current_app.config['TESTING']:
            smtp_encryption = get_settings()['smtp_encryption']
            if smtp_encryption == 'tls':
                smtp_encryption = 'required'
            elif smtp_encryption == 'ssl':
                smtp_encryption = 'ssl'
            elif smtp_encryption == 'tls_optional':
                smtp_encryption = 'optional'
            else:
                smtp_encryption = 'none'

            smtp_config = {
                'host': get_settings()['smtp_host'],
                'username': get_settings()['smtp_username'],
                'password': get_settings()['smtp_password'],
                'encryption': smtp_encryption,
                'port': get_settings()['smtp_port'],
            }
            smtp_status = check_smtp_config(smtp_encryption)
            if smtp_status:
                if email_service == 'smtp':
                    send_email_task_smtp.delay(
                        payload=payload, headers=None, smtp_config=smtp_config
                    )
                else:
                    key = get_settings().get('sendgrid_key')
                    if key:
                        headers = {
                            "Authorization": ("Bearer " + key),
                            "Content-Type": "application/json",
                        }
                        payload['fromname'] = email_from_name
                        send_email_task_sendgrid.delay(
                            payload=payload, headers=headers, smtp_config=smtp_config
                        )
                    else:
                        logging.exception(
                            'SMTP & sendgrid have not been configured properly'
                        )

            else:
                logging.exception('SMTP is not configured properly. Cannot send email.')
        # record_mail(to, action, subject, html)
        mail = Mail(
            recipient=to,
            action=action,
            subject=subject,
            message=html,
            time=datetime.utcnow(),
        )

        save_to_db(mail, 'Mail Recorded')
        record_activity('mail_event', email=to, action=action, subject=subject)
    return True


def send_email_with_action(user, action, **kwargs):
    """
    A general email helper to use in the APIs
    :param user: email or user to which email is to be sent
    :param action:
    :param kwargs:
    :return:
    """
    if isinstance(user, User):
        user = user.email

    send_email(
        to=user,
        action=action,
        subject=MAILS[action]['subject'].format(**kwargs),
        html=MAILS[action]['message'].format(**kwargs),
    )


def send_email_confirmation(email, link):
    """account confirmation"""
    send_email(
        to=email,
        action=USER_CONFIRM,
        subject=MAILS[USER_CONFIRM]['subject'],
        html=MAILS[USER_CONFIRM]['message'].format(email=email, link=link),
    )


def send_email_new_session(email, event_name, link):
    """email for new session"""
    send_email(
        to=email,
        action=NEW_SESSION,
        subject=MAILS[NEW_SESSION]['subject'].format(event_name=event_name),
        html=MAILS[NEW_SESSION]['message'].format(
            email=email, event_name=event_name, link=link
        ),
    )


def send_email_session_accept_reject(email, session, link):
    """email for new session"""
    session_name = session.title
    session_acceptance = session.state
    send_email(
        to=email,
        action=SESSION_ACCEPT_REJECT,
        subject=MAILS[SESSION_ACCEPT_REJECT]['subject'].format(
            session_name=session_name, acceptance=session_acceptance
        ),
        html=MAILS[SESSION_ACCEPT_REJECT]['message'].format(
            email=email,
            session_name=session_name,
            acceptance=session_acceptance,
            link=link,
        ),
    )


def send_email_role_invite(email, role_name, event_name, link):
    """email for role invite"""
    send_email(
        to=email,
        action=EVENT_ROLE,
        subject=MAILS[EVENT_ROLE]['subject'].format(role=role_name, event=event_name),
        html=MAILS[EVENT_ROLE]['message'].format(
            email=email, role=role_name, event=event_name, link=link
        ),
    )


def send_user_email_role_invite(email, role_name, event_name, link):
    """email for role invite"""
    send_email(
        to=email,
        action=USER_EVENT_ROLE,
        subject=MAILS[USER_EVENT_ROLE]['subject'].format(
            role=role_name, event=event_name
        ),
        html=MAILS[USER_EVENT_ROLE]['message'].format(
            email=email, role=role_name, event=event_name, link=link
        ),
    )


def send_email_after_event(email, event_name, frontend_url):
    """email for role invite"""
    send_email(
        to=email,
        action=AFTER_EVENT,
        subject=MAILS[AFTER_EVENT]['subject'].format(event_name=event_name),
        html=MAILS[AFTER_EVENT]['message'].format(
            email=email, event_name=event_name, url=frontend_url
        ),
    )


def send_email_for_monthly_fee_payment(
    email, event_name, previous_month, amount, app_name, link
):
    """email for monthly fee payment"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_EMAIL]['subject'].format(
            date=previous_month, event_name=event_name
        ),
        html=MAILS[MONTHLY_PAYMENT_EMAIL]['message'].format(
            email=email,
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
            payment_url=link,
        ),
    )


def send_followup_email_for_monthly_fee_payment(
    email, event_name, previous_month, amount, app_name, link
):
    """followup email for monthly fee payment"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['subject'].format(
            date=previous_month, event_name=event_name
        ),
        html=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['message'].format(
            email=email,
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
            payment_url=link,
        ),
    )


def send_export_mail(email, event_name, error_text=None, download_url=None):
    """followup export link in email"""
    if error_text:
        send_email(
            to=email,
            action=EVENT_EXPORT_FAIL,
            subject=MAILS[EVENT_EXPORT_FAIL]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_EXPORT_FAIL]['message'].format(error_text=error_text),
        )
    elif download_url:
        send_email(
            to=email,
            action=EVENT_EXPORTED,
            subject=MAILS[EVENT_EXPORTED]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_EXPORTED]['message'].format(download_url=download_url),
        )


def send_import_mail(email, event_name=None, error_text=None, event_url=None):
    """followup export link in email"""
    if error_text:
        send_email(
            to=email,
            action=EVENT_IMPORT_FAIL,
            subject=MAILS[EVENT_IMPORT_FAIL]['subject'],
            html=MAILS[EVENT_IMPORT_FAIL]['message'].format(error_text=error_text),
        )
    elif event_url:
        send_email(
            to=email,
            action=EVENT_IMPORTED,
            subject=MAILS[EVENT_IMPORTED]['subject'].format(event_name=event_name),
            html=MAILS[EVENT_IMPORTED]['message'].format(event_url=event_url),
        )


def send_test_email(recipient):
    send_email(
        to=recipient,
        action=TEST_MAIL,
        subject=MAILS[TEST_MAIL]['subject'],
        html=MAILS[TEST_MAIL]['message'],
    )


def send_email_change_user_email(user, email):
    serializer = get_serializer()
    hash_ = str(
        base64.b64encode(bytes(serializer.dumps([email, str_generator()]), 'utf-8')),
        'utf-8',
    )
    link = make_frontend_url('/email/verify'.format(id=user.id), {'token': hash_})
    send_email_with_action(user.email, USER_CONFIRM, email=user.email, link=link)
    send_email_with_action(email, USER_CHANGE_EMAIL, email=email, new_email=user.email)


def send_email_to_attendees(order, purchaser_id, attachments=None):
    for holder in order.ticket_holders:
        if holder.user and holder.user.id == purchaser_id:
            # Ticket holder is the purchaser
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED,
                subject=MAILS[TICKET_PURCHASED]['subject'].format(
                    event_name=order.event.name,
                    invoice_id=order.invoice_number,
                    frontend_url=get_settings()['frontend_url'],
                ),
                html=MAILS[TICKET_PURCHASED]['message'].format(
                    event_name=order.event.name,
                    frontend_url=get_settings()['frontend_url'],
                ),
                attachments=attachments,
            )
        else:
            # The Ticket holder is not the purchaser
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED_ATTENDEE,
                subject=MAILS[TICKET_PURCHASED_ATTENDEE]['subject'].format(
                    event_name=order.event.name, invoice_id=order.invoice_number
                ),
                html=MAILS[TICKET_PURCHASED_ATTENDEE]['message'].format(
                    my_tickets_url=get_settings()['frontend_url'] + '/my-tickets',
                    event_name=order.event.name,
                ),
                attachments=attachments,
            )


def send_order_cancel_email(order):
    cancel_msg = ''
    if order.cancel_note:
        cancel_msg = u"<br/>Message from the organizer: {cancel_note}".format(
            cancel_note=order.cancel_note
        )

    send_email(
        to=order.user.email,
        action=TICKET_CANCELLED,
        subject=MAILS[TICKET_CANCELLED]['subject'].format(
            event_name=order.event.name, invoice_id=order.invoice_number,
        ),
        html=MAILS[TICKET_CANCELLED]['message'].format(
            event_name=order.event.name,
            frontend_url=get_settings()['frontend_url'],
            cancel_msg=cancel_msg,
            app_name=get_settings()['app_name'],
        ),
    )

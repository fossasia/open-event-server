import base64
from datetime import datetime

from flask import current_app

from app import get_settings
from app.api.helpers.db import save_to_db
from app.api.helpers.files import make_frontend_url
from app.api.helpers.log import record_activity
from app.api.helpers.system_mails import MAILS
from app.api.helpers.utilities import string_empty, get_serializer, str_generator
from app.models.mail import Mail, USER_CONFIRM, NEW_SESSION, USER_CHANGE_EMAIL, SESSION_ACCEPT_REJECT, EVENT_ROLE, \
    AFTER_EVENT, MONTHLY_PAYMENT_EMAIL, MONTHLY_PAYMENT_FOLLOWUP_EMAIL, EVENT_EXPORTED, EVENT_EXPORT_FAIL, \
    EVENT_IMPORTED, EVENT_IMPORT_FAIL, TICKET_PURCHASED_ATTENDEE, TICKET_CANCELLED, TICKET_PURCHASED
from app.models.user import User


def send_email(to, action, subject, html):
    """
    Sends email and records it in DB
    """
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

                from .tasks import send_mail_via_smtp_task
                send_mail_via_smtp_task.delay(config, payload)
            else:
                payload['fromname'] = email_from_name
                key = get_settings()['sendgrid_key']
                if not key:
                    print('Sendgrid key not defined')
                    return
                headers = {
                    "Authorization": ("Bearer " + key),
                    "Content-Type": "application/json"
                }
                from .tasks import send_email_task
                send_email_task.delay(payload, headers)

        # record_mail(to, action, subject, html)
        mail = Mail(
            recipient=to, action=action, subject=subject,
            message=html, time=datetime.utcnow()
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
        html=MAILS[action]['message'].format(**kwargs)
    )


def send_email_confirmation(email, link):
    """account confirmation"""
    send_email(
        to=email,
        action=USER_CONFIRM,
        subject=MAILS[USER_CONFIRM]['subject'],
        html=MAILS[USER_CONFIRM]['message'].format(
            email=email, link=link
        )
    )


def send_email_new_session(email, event_name, link):
    """email for new session"""
    send_email(
        to=email,
        action=NEW_SESSION,
        subject=MAILS[NEW_SESSION]['subject'].format(
            event_name=event_name
        ),
        html=MAILS[NEW_SESSION]['message'].format(
            email=email,
            event_name=event_name,
            link=link
        )
    )


def send_email_session_accept_reject(email, session, link):
    """email for new session"""
    session_name = session.title
    session_acceptance = session.state
    send_email(
        to=email,
        action=SESSION_ACCEPT_REJECT,
        subject=MAILS[SESSION_ACCEPT_REJECT]['subject'].format(
            session_name=session_name,
            acceptance=session_acceptance
        ),
        html=MAILS[SESSION_ACCEPT_REJECT]['message'].format(
            email=email,
            session_name=session_name,
            acceptance=session_acceptance,
            link=link
        )
    )


def send_email_role_invite(email, role_name, event_name, link):
    """email for role invite"""
    send_email(
        to=email,
        action=EVENT_ROLE,
        subject=MAILS[EVENT_ROLE]['subject'].format(
            role=role_name,
            event=event_name
        ),
        html=MAILS[EVENT_ROLE]['message'].format(
            email=email,
            role=role_name,
            event=event_name,
            link=link
        )
    )


def send_email_after_event(email, event_name, upcoming_events):
    """email for role invite"""
    send_email(
        to=email,
        action=AFTER_EVENT,
        subject=MAILS[AFTER_EVENT]['subject'].format(
            event_name=event_name
        ),
        html=MAILS[AFTER_EVENT]['message'].format(
            email=email,
            event_name=event_name,
            upcoming_events=upcoming_events
        )
    )


def send_email_for_monthly_fee_payment(email, event_name, previous_month, amount, app_name, link):
    """email for monthly fee payment"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_EMAIL]['subject'].format(
            date=previous_month,
            event_name=event_name
        ),
        html=MAILS[MONTHLY_PAYMENT_EMAIL]['message'].format(
            email=email,
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
            payment_url=link
        )
    )


def send_followup_email_for_monthly_fee_payment(email, event_name, previous_month, amount, app_name, link):
    """followup email for monthly fee payment"""
    send_email(
        to=email,
        action=MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
        subject=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['subject'].format(
            date=previous_month,
            event_name=event_name
        ),
        html=MAILS[MONTHLY_PAYMENT_FOLLOWUP_EMAIL]['message'].format(
            email=email,
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
            payment_url=link
        )
    )


def send_export_mail(email, event_name, error_text=None, download_url=None):
    """followup export link in email"""
    if error_text:
        send_email(
            to=email,
            action=EVENT_EXPORT_FAIL,
            subject=MAILS[EVENT_EXPORT_FAIL]['subject'].format(
                event_name=event_name
            ),
            html=MAILS[EVENT_EXPORT_FAIL]['message'].format(
                error_text=error_text
            )
        )
    elif download_url:
        send_email(
            to=email,
            action=EVENT_EXPORTED,
            subject=MAILS[EVENT_EXPORTED]['subject'].format(
                event_name=event_name
            ),
            html=MAILS[EVENT_EXPORTED]['message'].format(
                download_url=download_url
            )
        )


def send_import_mail(email, event_name=None, error_text=None, event_url=None):
    """followup export link in email"""
    if error_text:
        send_email(
            to=email,
            action=EVENT_IMPORT_FAIL,
            subject=MAILS[EVENT_IMPORT_FAIL]['subject'],
            html=MAILS[EVENT_IMPORT_FAIL]['message'].format(
                error_text=error_text
            )
        )
    elif event_url:
        send_email(
            to=email,
            action=EVENT_IMPORTED,
            subject=MAILS[EVENT_IMPORTED]['subject'].format(
                event_name=event_name
            ),
            html=MAILS[EVENT_IMPORTED]['message'].format(
                event_url=event_url
            )
        )


def send_email_change_user_email(user, email):
    serializer = get_serializer()
    hash_ = str(base64.b64encode(bytes(serializer.dumps([email, str_generator()]), 'utf-8')), 'utf-8')
    link = make_frontend_url('/email/verify'.format(id=user.id), {'token': hash_})
    send_email_with_action(user.email, USER_CONFIRM, email=user.email, link=link)
    send_email_with_action(email, USER_CHANGE_EMAIL, email=email, new_email=user.email)


def send_email_to_attendees(order, purchaser_id):
    for holder in order.ticket_holders:
        if holder.user and holder.user.id == purchaser_id:
            # Ticket holder is the purchaser
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED,
                subject=MAILS[TICKET_PURCHASED]['subject'].format(
                    event_name=order.event.name,
                    invoice_id=order.invoice_number
                ),
                html=MAILS[TICKET_PURCHASED]['message'].format(
                    pdf_url=holder.pdf_url,
                    event_name=order.event.name
                )
            )
        else:
            # The Ticket holder is not the purchaser
            send_email(
                to=holder.email,
                action=TICKET_PURCHASED_ATTENDEE,
                subject=MAILS[TICKET_PURCHASED_ATTENDEE]['subject'].format(
                    event_name=order.event.name,
                    invoice_id=order.invoice_number
                ),
                html=MAILS[TICKET_PURCHASED_ATTENDEE]['message'].format(
                    pdf_url=holder.pdf_url,
                    event_name=order.event.name
                )
            )


def send_order_cancel_email(order):
    send_email(
        to=order.user.email,
        action=TICKET_CANCELLED,
        subject=MAILS[TICKET_CANCELLED]['subject'].format(
            event_name=order.event.name,
            invoice_id=order.invoice_number
        ),
        html=MAILS[TICKET_CANCELLED]['message'].format(
            event_name=order.event.name,
            order_url=make_frontend_url('/orders/{identifier}'.format(identifier=order.identifier)),
            cancel_note=order.cancel_note
        )
    )

import base64
import logging
from datetime import datetime
from itertools import groupby
from typing import Dict

from flask import current_app, render_template
from sqlalchemy.orm import joinedload

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
    MONTHLY_PAYMENT_POST_DUE_EMAIL,
    MONTHLY_PAYMENT_PRE_DUE_EMAIL,
    NEW_SESSION,
    SESSION_STATE_CHANGE,
    TEST_MAIL,
    TICKET_CANCELLED,
    TICKET_PURCHASED,
    TICKET_PURCHASED_ATTENDEE,
    TICKET_PURCHASED_ORGANIZER,
    USER_CHANGE_EMAIL,
    USER_CONFIRM,
    USER_EVENT_ROLE,
    Mail,
)
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.settings import get_settings

logger = logging.getLogger(__name__)
# pytype: disable=attribute-error


def check_smtp_config(config):
    """
    Checks config of SMTP
    """
    for field in config:
        if field is None:
            return False
    return True


def send_email(to, action, subject, html, attachments=None, bcc=None):
    """
    Sends email and records it in DB
    """
    from .tasks import get_smtp_config, send_email_task_sendgrid, send_email_task_smtp

    if isinstance(to, User):
        logger.warning('to argument should be an email string, not a User object')
        to = to.email

    if string_empty(to):
        logger.warning('Recipient cannot be empty')
        return False
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
        'bcc': bcc,
    }

    if not (current_app.config['TESTING'] or email_service == 'disable'):
        if email_service == 'smtp':
            smtp_status = check_smtp_config(get_smtp_config())
            if smtp_status:
                send_email_task_smtp.delay(payload)
            else:
                logger.error('SMTP is not configured properly. Cannot send email.')
        elif email_service == 'sendgrid':
            key = get_settings().get('sendgrid_key')
            if key:
                payload['fromname'] = email_from_name
                send_email_task_sendgrid.delay(payload)
            else:
                logger.error('SMTP & sendgrid have not been configured properly')
        else:
            logger.error(
                'Invalid Email Service Setting: %s. Skipping email', email_service
            )
    else:
        logger.warning('Email Service is disabled in settings, so skipping email')

    mail_recorder = current_app.config['MAIL_RECORDER']
    mail_recorder.record(payload)

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


def send_email_with_action(user, action, bcc=None, **kwargs):
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
        bcc=bcc,
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


def send_email_session_state_change(email, session, mail_override: Dict[str, str]=None):
    """email for new session"""
    event = session.event

    settings = get_settings()
    app_name = settings['app_name']
    frontend_url = settings['frontend_url']

    context = {
        'session_name': session.title,
        'session_link': session.site_link,
        'session_state': session.state,
        'event_name': event.name,
        'event_link': event.site_link,
        'app_name': app_name,
        'frontend_link': frontend_url,
    }

    try:
        mail = MAILS[SESSION_STATE_CHANGE][session.state]
        if mail_override:
            mail = mail.copy()
            mail['subject'] = mail_override.get('subject') or mail['subject']
            mail['message'] = mail_override.get('message') or mail['message']
            mail['bcc'] = mail_override.get('bcc', [])
    except KeyError:
        logger.error('No mail found for session state change: ' + session.state)
        return

    send_email(
        to=email,
        action=SESSION_STATE_CHANGE,
        subject=mail['subject'].format(**context),
        html=mail['message'].format(**context),
        bcc=mail['bcc']
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
    user, event_name, previous_month, amount, app_name, link, follow_up=False
):
    """email for monthly fee payment"""
    options = {
        False: MONTHLY_PAYMENT_EMAIL,
        True: MONTHLY_PAYMENT_FOLLOWUP_EMAIL,
        'pre_due': MONTHLY_PAYMENT_PRE_DUE_EMAIL,
        'post_due': MONTHLY_PAYMENT_POST_DUE_EMAIL,
    }
    key = options[follow_up]
    email = user.email
    send_email(
        to=email,
        action=key,
        subject=MAILS[key]['subject'].format(
            date=previous_month, event_name=event_name, app_name=app_name
        ),
        html=MAILS[key]['message'].format(
            name=user.full_name,
            email=email,
            event_name=event_name,
            date=previous_month,
            amount=amount,
            app_name=app_name,
            payment_url=link,
        ),
        bcc=get_settings()['admin_billing_email'],
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
    link = make_frontend_url('/email/verify', {'token': hash_})
    send_email_with_action(user.email, USER_CONFIRM, email=user.email, link=link)
    send_email_with_action(email, USER_CHANGE_EMAIL, email=email, new_email=user.email)


def send_email_to_attendees(order):
    attachments = None
    if current_app.config['ATTACH_ORDER_PDF']:
        attachments = [order.ticket_pdf_path, order.invoice_pdf_path]

    attendees = (
        TicketHolder.query.options(
            joinedload(TicketHolder.ticket), joinedload(TicketHolder.user)
        )
        .filter_by(order_id=order.id)
        .all()
    )
    email_group = groupby(attendees, lambda a: a.email)

    event = order.event
    context = dict(
        order=order,
        settings=get_settings(),
        order_view_url=order.site_view_link,
    )

    buyer_email = order.user.email
    send_email(
        to=buyer_email,
        action=TICKET_PURCHASED,
        subject=MAILS[TICKET_PURCHASED]['subject'].format(
            event_name=event.name,
            invoice_id=order.invoice_number,
        ),
        html=render_template(
            'email/ticket_purchased.html', attendees=attendees, **context
        ),
        attachments=attachments,
    )

    for email, attendees_group in email_group:
        if email == buyer_email:
            # Ticket holder is the purchaser
            continue

        # The Ticket holder is not the purchaser
        send_email(
            to=email,
            action=TICKET_PURCHASED_ATTENDEE,
            subject=MAILS[TICKET_PURCHASED_ATTENDEE]['subject'].format(
                event_name=event.name,
                invoice_id=order.invoice_number,
            ),
            html=render_template(
                'email/ticket_purchased_attendee.html',
                attendees=list(attendees_group),
                **context,
            ),
            attachments=attachments,
        )


def send_order_purchase_organizer_email(order, recipients):
    context = dict(
        buyer_email=order.user.email,
        event_name=order.event.name,
        invoice_id=order.invoice_number,
        frontend_url=get_settings()['frontend_url'],
        order_url=order.site_view_link,
    )
    emails = list({organizer.email for organizer in recipients})
    if emails:
        send_email_with_action(
            emails[0], TICKET_PURCHASED_ORGANIZER, bcc=emails[1:], **context
        )


def send_order_cancel_email(order):
    cancel_msg = ''
    if order.cancel_note:
        cancel_msg = "<br/>Message from the organizer: {cancel_note}".format(
            cancel_note=order.cancel_note
        )

    send_email(
        to=order.user.email,
        action=TICKET_CANCELLED,
        subject=MAILS[TICKET_CANCELLED]['subject'].format(
            event_name=order.event.name,
            invoice_id=order.invoice_number,
        ),
        html=MAILS[TICKET_CANCELLED]['message'].format(
            event_name=order.event.name,
            frontend_url=get_settings()['frontend_url'],
            cancel_msg=cancel_msg,
            app_name=get_settings()['app_name'],
        ),
    )

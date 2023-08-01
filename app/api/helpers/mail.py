import base64
import datetime
import logging
import os
from itertools import groupby
from typing import Dict, Optional

import pytz
from babel.dates import format_date, format_datetime, format_time
from babel.numbers import format_currency
from flask import current_app, render_template
from sqlalchemy.orm import joinedload

from app.api.helpers.db import save_to_db
from app.api.helpers.files import generate_ics_file, make_frontend_url
from app.api.helpers.log import record_activity
from app.api.helpers.system_mails import MAILS, MailType
from app.api.helpers.utilities import get_serializer, str_generator, string_empty
from app.models.event import Event
from app.models.mail import Mail
from app.models.message_setting import MessageSettings
from app.models.order import OrderTicket
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


def send_email(to, action, subject, html, attachments=None, bcc=None, reply_to=None):
    """
    Sends email and records it in DB
    """
    from .tasks import get_smtp_config, send_email_task_sendgrid, send_email_task_smtp

    if not MessageSettings.is_enabled(action):
        logger.info("Mail of type %s is not enabled. Hence, skipping...", action)
        return

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
        'reply_to': reply_to,
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
    )

    save_to_db(mail, 'Mail Recorded')
    record_activity('mail_event', email=to, action=action, subject=subject)

    return True


def send_email_with_action(user, action, template_name, bcc=None, **kwargs):
    """
    A general email helper to use in the APIs
    :param user: email or user to which email is to be sent
    :param action:
    :param kwargs:
    :return:
    """
    if not MessageSettings.is_enabled(action):
        logger.info("Mail of type %s is not enabled. Hence, skipping...", action)
        return

    if isinstance(user, User):
        user = user.email

    template_path = 'email/' + template_name.lower() + '.html'

    send_email(
        to=user,
        action=action,
        subject=MAILS[action]['subject'].format(**kwargs),
        html=render_template(template_path, **kwargs),
        bcc=bcc,
    )


def send_email_confirmation(email, link):
    """account confirmation"""
    action = MailType.USER_CONFIRM
    app_name = get_settings()['app_name']
    mail = MAILS[action]
    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(app_name=app_name),
        html=render_template(mail['template'], email=email, link=link),
    )


def send_email_new_session(email, session, speakers):
    """email for new session"""
    app_name = get_settings()['app_name']
    front_page = get_settings()['frontend_url']
    session_overview_link = session.event.organizer_site_link + "/sessions/pending"
    action = MailType.NEW_SESSION
    mail = MAILS[action]
    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(session=session),
        html=render_template(
            mail['template'],
            session=session,
            speakers=speakers,
            session_overview_link=session_overview_link,
            app_name=app_name,
            front_page=front_page,
        ),
    )


def send_email_ticket_sales_end(event, emails):
    """email for ticket sales end"""
    action = MailType.TICKET_SALES_END
    mail = MAILS[action]
    settings = get_settings()
    tickets = []
    for ticket in event.tickets:
        if ticket.sales_ends_at.date() == (
            datetime.date.today() - datetime.timedelta(days=1)
        ):
            tickets.append(ticket.name)

    ticket_names = ", ".join(tickets)

    event_dashboard = settings['frontend_url'] + '/events/' + event.identifier
    if len(emails) > 0:
        send_email(
            to=emails[0],
            action=action,
            subject=mail['subject'].format(event_name=event.name),
            html=render_template(
                mail['template'],
                settings=settings,
                event_dashboard=event_dashboard,
                event_name=event.name,
                ticket_names=ticket_names,
            ),
            bcc=emails[1:],
            reply_to=emails[-1],
        )


def send_email_ticket_sales_end_tomorrow(event, emails):
    """email for ticket sales end"""
    action = MailType.TICKET_SALES_END_TOMORROW
    mail = MAILS[action]
    settings = get_settings()
    tickets = []
    for ticket in event.tickets:
        if ticket.sales_ends_at.date() == (
            datetime.date.today() - datetime.timedelta(days=-1)
        ):
            tickets.append(ticket.name)

    ticket_names = ", ".join(tickets)

    event_dashboard = settings['frontend_url'] + '/events/' + event.identifier
    if len(emails) > 0:
        send_email(
            to=emails[0],
            action=action,
            subject=mail['subject'].format(event_name=event.name),
            html=render_template(
                mail['template'],
                settings=settings,
                event_dashboard=event_dashboard,
                event_name=event.name,
                ticket_names=ticket_names,
            ),
            bcc=emails[1:],
            reply_to=emails[-1],
        )


def send_email_ticket_sales_end_next_week(event, emails):
    """email for ticket sales end"""
    action = MailType.TICKET_SALES_END_NEXT_WEEK
    mail = MAILS[action]
    settings = get_settings()
    tickets = []
    for ticket in event.tickets:
        if ticket.sales_ends_at.date() == (
            datetime.date.today() - datetime.timedelta(days=-7)
        ):
            tickets.append(ticket.name)

    ticket_names = ", ".join(tickets)

    event_dashboard = settings['frontend_url'] + '/events/' + event.identifier
    if len(emails) > 0:
        send_email(
            to=emails[0],
            action=action,
            subject=mail['subject'].format(event_name=event.name),
            html=render_template(
                mail['template'],
                settings=settings,
                event_dashboard=event_dashboard,
                event_name=event.name,
                ticket_names=ticket_names,
            ),
            bcc=emails[1:],
            reply_to=emails[-1],
        )


def send_email_session_state_change(
    email, session, mail_override: Optional[Dict[str, str]] = None
):
    """email for new session"""
    event = session.event

    settings = get_settings()
    app_name = settings['app_name']
    frontend_url = settings['frontend_url']
    context = {
        'session_name': session.title,
        'session_link': session.site_link,
        'session_cfs_link': session.site_cfs_link,
        'session_state': session.state,
        'event_name': event.name,
        'event_link': event.site_link,
        'app_name': app_name,
        'frontend_link': frontend_url,
    }

    try:
        mail = MAILS[MailType.SESSION_STATE_CHANGE][session.state]
        if mail_override:
            mail = mail.copy()
            mail['subject'] = mail_override.get('subject') or mail['subject']
            mail['message'] = mail_override.get('message') or mail['message']
            mail['bcc'] = mail_override.get('bcc', [])
    except KeyError:
        logger.error('No mail found for session state change: ' + session.state)
        return

    organizers_email = list(
        map(
            lambda x: x.email,
            session.event.organizers + session.event.coorganizers + [session.event.owner],
        )
    )
    bcc = list(set(organizers_email + mail.get('bcc', [])))
    if email in bcc:
        bcc.remove(email)  # to, cc, bcc should have unique emails

    send_email(
        to=email,
        action=MailType.SESSION_STATE_CHANGE,
        subject=mail['subject'].format(**context),
        html=mail['message'].format(**context),
        bcc=bcc,
        reply_to=session.event.owner.email,
    )


def send_email_role_invite(email, role_name, event_name, link):
    """email for role invite"""
    action = MailType.EVENT_ROLE
    mail = MAILS[action]
    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(role=role_name, event=event_name),
        html=render_template(
            mail['template'],
            email=email,
            role=role_name,
            event=event_name,
            link=link,
        ),
    )


def send_email_speaker_invite(email, session, cfs_link, inviter):
    """email for speaker invite"""
    action = MailType.SPEAKER_INVITE
    app_name = get_settings()['app_name']
    mail = MAILS[action]
    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(session=session.title),
        html=render_template(
            mail['template'],
            session_title=session.title,
            event_name=session.event.name,
            event_link=session.event.site_link,
            app_name=app_name,
            frontend_url=get_settings()['frontend_url'],
            inviter_email=inviter.email,
            inviter_name=inviter.name,
            cfs_link=cfs_link,
        ),
    )


def send_email_group_role_invite(email, role_name, group_name, link):
    """email for role invite"""
    action = MailType.GROUP_ROLE
    mail = MAILS[action]
    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(role=role_name, group=group_name),
        html=render_template(
            mail['template'],
            email=email,
            role=role_name,
            group=group_name,
            link=link,
        ),
    )


def send_email_announce_event(event, group, emails):
    """email for announce event"""

    action = MailType.ANNOUNCE_EVENT
    mail = MAILS[action]

    event_name = event.name
    group_name = group.name
    event_date = event.starts_at
    event_description = event.description
    event_url = event.site_link
    event_location = event.normalized_location
    event_time = event.starts_at
    group_url = group.view_page_link
    app_name = get_settings()['app_name']

    if len(emails) > 0:
        for email in emails:
            send_email(
                to=email,
                action=action,
                subject=mail['subject'].format(
                    event_name=event_name,
                    group_name=group_name,
                    event_date=convert_to_user_locale(email, date=event_date),
                ),
                html=render_template(
                    mail['template'],
                    event_name=event_name,
                    event_description=event_description,
                    event_url=event_url,
                    event_location=event_location,
                    event_date=convert_to_user_locale(email, date=event_date),
                    event_time=convert_to_user_locale(
                        email, time=event_time, tz=event.timezone
                    ),
                    group_name=group_name,
                    group_url=group_url,
                    app_name=app_name,
                ),
            )


def send_email_for_monthly_fee_payment(
    user, event_name, previous_month, amount, app_name, link, follow_up=False
):
    """email for monthly fee payment"""
    options = {
        False: MailType.MONTHLY_PAYMENT,
        True: MailType.MONTHLY_PAYMENT_FOLLOWUP,
        'pre_due': MailType.MONTHLY_PAYMENT_PRE_DUE,
        'post_due': MailType.MONTHLY_PAYMENT_POST_DUE,
    }
    key = options[follow_up]
    mail = MAILS[key]
    email = user.email
    invoice_url = make_frontend_url('/account/billing/invoices')
    send_email(
        to=email,
        action=key,
        subject=mail['subject'].format(
            date=previous_month, event_name=event_name, app_name=app_name
        ),
        html=render_template(
            mail['template'],
            name=user.full_name,
            email=email,
            event_name=event_name,
            invoice_url=invoice_url,
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
        action = MailType.EVENT_EXPORT_FAIL
        mail = MAILS[action]
        send_email(
            to=email,
            action=action,
            subject=mail['subject'].format(event_name=event_name),
            html=render_template(mail['template'], error_text=error_text),
        )
    elif download_url:
        action = MailType.EVENT_EXPORTED
        mail = MAILS[action]
        send_email(
            to=email,
            action=action,
            subject=mail['subject'].format(event_name=event_name),
            html=render_template(mail['template'], download_url=download_url),
        )


def send_import_mail(email, event_name=None, error_text=None, event_url=None):
    """followup export link in email"""
    if error_text:
        action = MailType.EVENT_IMPORT_FAIL
        mail = MAILS[action]
        send_email(
            to=email,
            action=action,
            subject=mail['subject'],
            html=render_template(mail['template'], error_text=error_text),
        )
    elif event_url:
        action = MailType.EVENT_IMPORTED
        mail = MAILS[action]
        send_email(
            to=email,
            action=action,
            subject=mail['subject'].format(event_name=event_name),
            html=render_template(mail['template'], event_url=event_url),
        )


def send_test_email(recipient):
    send_email(
        to=recipient,
        action=MailType.TEST_MAIL,
        subject=MAILS[MailType.TEST_MAIL]['subject'],
        html=MAILS[MailType.TEST_MAIL]['message'],
    )


def send_email_change_user_email(user, email):
    serializer = get_serializer()
    hash_ = str(
        base64.b64encode(bytes(serializer.dumps([email, str_generator()]), 'utf-8')),
        'utf-8',
    )
    app_name = get_settings()['app_name']
    link = make_frontend_url('/email/verify', {'token': hash_})
    send_email_with_action(
        user.email,
        MailType.USER_CONFIRM,
        'user_confirm',
        email=user.email,
        link=link,
        app_name=app_name,
    )
    send_email_with_action(
        email,
        MailType.USER_CHANGE_EMAIL,
        'user_change_email',
        email=email,
        new_email=user.email,
    )


def send_email_to_attendees(order):
    attachments = None
    if current_app.config['ATTACH_ORDER_PDF']:
        attachments = [order.ticket_pdf_path, order.invoice_pdf_path]

    event = order.event
    ical_file_path = generate_ics_file(event.id, include_sessions=False)

    if os.path.exists(ical_file_path):
        if attachments is None:
            attachments = [ical_file_path]
        else:
            attachments.append(ical_file_path)

    attendees = (
        TicketHolder.query.options(
            joinedload(TicketHolder.ticket), joinedload(TicketHolder.user)
        )
        .filter_by(order_id=order.id)
        .all()
    )
    email_group = groupby(attendees, lambda a: a.email)

    buyer_email = order.user.email
    event_date = convert_to_user_locale(
        buyer_email,
        date=order.event.starts_at,
    )
    event_end_date = convert_to_user_locale(
        buyer_email,
        date_time=order.event.ends_at,
        tz=order.event.timezone,
    )
    event_time = convert_to_user_locale(
        buyer_email,
        time=order.event.starts_at,
        tz=order.event.timezone,
    )

    context = dict(
        order=order,
        starts_at=convert_to_user_locale(
            buyer_email,
            date_time=order.event.starts_at,
            tz=order.event.timezone,
        ),
        ends_at=event_end_date,
        event_time=event_time,
        settings=get_settings(),
        order_view_url=order.site_view_link,
    )

    action = MailType.TICKET_PURCHASED
    mail = MAILS[action]
    send_email(
        to=buyer_email,
        action=action,
        subject=mail['subject'].format(
            event_name=event.name,
            invoice_id=order.invoice_number,
            event_date=event_date,
            event_time=event_time,
        ),
        html=render_template(mail['template'], attendees=attendees, **context),
        attachments=attachments,
    )

    action = MailType.TICKET_PURCHASED_ATTENDEE
    mail = MAILS[action]
    for email, attendees_group in email_group:
        if email == buyer_email:
            # Ticket holder is the purchaser
            continue

        # The Ticket holder is not the purchaser
        send_email(
            to=email,
            action=action,
            subject=mail['subject'].format(
                event_name=event.name,
                invoice_id=order.invoice_number,
                event_date=event_date,
                event_time=event_time,
            ),
            html=render_template(
                mail['template'],
                attendees=list(attendees_group),
                **context,
            ),
            attachments=attachments,
        )


def send_order_purchase_organizer_email(order, recipients):

    order_tickets = OrderTicket.query.filter_by(order_id=order.id).all()
    emails = list({organizer.email for organizer in recipients})
    print(emails[0])

    context = dict(
        buyer_email=order.user.email,
        buyer_name=order.user.full_name,
        event_name=order.event.name,
        invoice_id=order.invoice_number,
        frontend_url=get_settings()['frontend_url'],
        site_link=order.event.site_link,
        order_url=order.site_view_link,
        event_date=convert_to_user_locale(
            order.user.email,
            date=order.event.starts_at,
        ),
        event_time=convert_to_user_locale(
            order.user.email,
            time=order.event.starts_at,
            tz=order.event.timezone,
        ),
        timezone=order.event.timezone,
        purchase_time=convert_to_user_locale(
            emails[0], date_time=order.completed_at, tz=order.event.timezone
        ),
        payment_mode=order.payment_mode,
        payment_status=order.status,
        order_amount=convert_to_user_locale(
            emails[0], amount=order.amount, currency=order.event.payment_currency
        ),
        tickets_count=order.tickets_count,
        order_tickets=order_tickets,
        buyer_org=order.company,
        buyer_address=order.address,
        buyer_zipcode=order.zipcode,
        buyer_city=order.city,
        buyer_state=order.state,
        buyer_country=order.country,
        buyer_tax_id=order.tax_business_info,
        app_name=get_settings()['app_name'],
    )
    if emails:
        send_email_with_action(
            emails[0],
            MailType.TICKET_PURCHASED_ORGANIZER,
            'ticket_purchased_organizer',
            bcc=emails[1:],
            **context,
        )


def send_order_cancel_email(order):
    cancel_msg = ''
    if order.cancel_note:
        cancel_msg = "<br/>Message from the organizer: {cancel_note}".format(
            cancel_note=order.cancel_note
        )

    order_url = (
        get_settings()['frontend_url'] + '/orders/' + str(order.identifier) + '/view/'
    )
    event_url = get_settings()['frontend_url'] + '/e/' + order.event.identifier

    action = MailType.TICKET_CANCELLED
    mail = MAILS[action]
    send_email(
        to=order.user.email,
        action=action,
        subject=mail['subject'].format(
            event_name=order.event.name,
            invoice_id=order.invoice_number,
        ),
        html=render_template(
            mail['template'],
            event_name=order.event.name,
            order_url=order_url,
            event_url=event_url,
            cancel_msg=cancel_msg,
            app_name=get_settings()['app_name'],
        ),
    )


def send_password_change_email(user):
    action = MailType.PASSWORD_CHANGE
    mail = MAILS[action]
    send_email(
        to=user.email,
        action=action,
        subject=mail['subject'].format(app_name=get_settings()['app_name']),
        html=render_template(mail['template']),
    )


def send_password_reset_email(user):
    link = make_frontend_url('/reset-password', {'token': user.reset_password})
    action = (
        MailType.PASSWORD_RESET_AND_VERIFY
        if user.was_registered_with_order
        else MailType.PASSWORD_RESET
    )
    mail = MAILS[action]
    send_email(
        to=user.email,
        action=action,
        subject=mail['subject'].format(app_name=get_settings()['app_name']),
        html=render_template(
            mail['template'],
            link=link,
            settings=get_settings(),
            token=user.reset_password,
        ),
    )


def send_user_register_email(user):
    s = get_serializer()
    hash = str(
        base64.b64encode(str(s.dumps([user.email, str_generator()])).encode()),
        'utf-8',
    )
    link = make_frontend_url('/verify', {'token': hash})
    settings = get_settings()
    action = MailType.USER_REGISTER
    mail = MAILS[action]
    send_email(
        to=user.email,
        action=action,
        subject=mail['subject'].format(app_name=settings['app_name']),
        html=render_template(
            mail['template'],
            email=user.email,
            link=link,
            settings=get_settings(),
        ),
    )


def send_email_to_moderator(video_stream_moderator):
    action = MailType.VIDEO_MODERATOR_INVITE
    mail = MAILS[action]
    event = Event.query.get(video_stream_moderator.video_stream._event_id)
    send_email(
        to=video_stream_moderator.email,
        action=action,
        subject=mail['subject'].format(
            video_name=video_stream_moderator.video_stream.name, event_name=event.name
        ),
        html=render_template(
            mail['template'],
            registration_url=make_frontend_url('/register'),
            event_name=event.name,
            video_stream_name=video_stream_moderator.video_stream.name,
            user=video_stream_moderator.user,
            settings=get_settings(),
        ),
    )


def send_email_after_event(email, event_name):
    app_name = get_settings()['app_name']
    action = MailType.AFTER_EVENT
    mail = MAILS[action]

    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(event_name=event_name, app_name=app_name),
        html=render_template(
            mail['template'],
            app_name=app_name,
            email=email,
            eventname=event_name,
        ),
    )


def send_email_after_event_speaker(email, event_name):
    action = MailType.AFTER_EVENT_SPEAKER
    mail = MAILS[action]

    send_email(
        to=email,
        action=action,
        subject=mail['subject'].format(event_name=event_name),
        html=render_template(
            mail['template'],
            eventname=event_name,
            email=email,
        ),
    )


def convert_to_user_locale(
    email, date_time=None, date=None, time=None, tz=None, amount=None, currency=None
):
    """
    Convert date and time and amount to user selected language
    :return        : datetime/date/time translated to user locale
    """
    if email:
        user = User.query.filter(User.email == email).first()
        user_locale = 'en'

        if user and user.language_prefrence:
            user_locale = user.language_prefrence

        if amount and currency:
            return format_currency(amount, currency, locale=user_locale)

        if date_time and tz:
            return format_datetime(
                date_time, 'full', tzinfo=pytz.timezone(tz), locale=user_locale
            )

        if date:
            return format_date(date, 'd MMMM Y', locale=user_locale)

        if time and tz:
            return format_time(
                time, 'HH:mm (zzzz)', tzinfo=pytz.timezone(tz), locale=user_locale
            )

    return None

import base64
import csv
import logging
import os
import urllib.error
import uuid
from datetime import datetime

import pytz
import requests
from flask import current_app, render_template
from flask_celeryext import FlaskCeleryExt, RequestContextTask
from marrow.mailer import Mailer, Message
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import (
    Attachment,
    Disposition,
    FileContent,
    FileName,
    FileType,
    From,
    Mail,
)

from app.api.chat.rocket_chat import rename_rocketchat_room
from app.api.exports import event_export_task_base
from app.api.helpers.db import safe_query, save_to_db
from app.api.helpers.files import (
    create_save_image_sizes,
    create_save_pdf,
    create_save_resized_image,
    generate_ics_file,
)
from app.api.helpers.mail import check_smtp_config, send_export_mail, send_import_mail
from app.api.helpers.pentabarfxml import PentabarfExporter
from app.api.helpers.storage import UPLOAD_PATHS, UploadedFile, upload
from app.api.helpers.utilities import strip_tags
from app.api.helpers.xcal import XCalExporter
from app.api.imports import import_event_task_base
from app.instance import create_app
from app.models import db
from app.models.custom_form import CustomForms
from app.models.discount_code import DiscountCode
from app.models.event import Event
from app.models.exhibitor import Exhibitor
from app.models.group import Group
from app.models.order import Order
from app.models.session import Session
from app.models.speaker import Speaker
from app.models.sponsor import Sponsor
from app.models.ticket_holder import TicketHolder
from app.models.user import User
from app.models.user_follow_group import UserFollowGroup
from app.settings import get_settings

from .import_helpers import update_import_job

"""
Define all API v2 celery tasks here
This is done to resolve circular imports
"""


logger = logging.getLogger(__name__)


def make_celery(app=None):
    app = app or create_app()
    ext = FlaskCeleryExt(app)
    return ext.celery


celery = make_celery()


def get_smtp_config():
    smtp_encryption = get_settings()['smtp_encryption']
    if smtp_encryption == 'tls':
        smtp_encryption = 'required'
    elif smtp_encryption == 'ssl':
        smtp_encryption = 'ssl'
    elif smtp_encryption == 'tls_optional':
        smtp_encryption = 'optional'
    else:
        smtp_encryption = 'none'

    return {
        'host': get_settings()['smtp_host'],
        'username': get_settings()['smtp_username'],
        'password': get_settings()['smtp_password'],
        'tls': smtp_encryption,
        'port': get_settings()['smtp_port'],
    }


def empty_attachments_send(mail_client, message):
    """
    Empty attachments and send mail
    """
    logging.warning(
        "Attachments could not be sent. Sending confirmation mail without attachments..."
    )
    message.attachments = []
    mail_client.send(message)


@celery.task(name='send.email.post.sendgrid')
def send_email_task_sendgrid(payload):
    message = Mail(
        from_email=From(payload['from'], payload['fromname']),
        to_emails=payload['to'],
        subject=payload['subject'],
        html_content=payload["html"],
    )

    if payload['bcc'] is not None:
        message.bcc = payload['bcc']

    if payload['reply_to'] is not None:
        message.reply_to = payload['reply_to']

    if payload['attachments'] is not None:
        for filename in payload['attachments']:
            with open(filename, 'rb') as f:
                file_data = f.read()
                f.close()
            encoded = base64.b64encode(file_data).decode()
            attachment = Attachment()
            attachment.file_content = FileContent(encoded)
            attachment.disposition = Disposition('attachment')
            if filename.endswith('.pdf'):
                attachment.file_type = FileType('application/pdf')
                attachment.file_name = FileName(filename)
            elif filename.endswith('.ics'):
                attachment.file_type = FileType('text/calendar')
                attachment.file_name = FileName('ical.ics')
            message.add_attachment(attachment)
    sendgrid_client = SendGridAPIClient(get_settings()['sendgrid_key'])
    logging.info(
        'Sending an email to {} regarding "{}" on behalf of {}'.format(
            payload['to'], payload["subject"], payload["from"]
        )
    )
    try:
        sendgrid_client.send(message)
        logging.info('Email sent successfully')
    except urllib.error.HTTPError as e:
        if e.code == 429:
            logging.warning("Sendgrid quota has exceeded")
            send_email_task_smtp.delay(payload)
        elif e.code == 554:
            empty_attachments_send(sendgrid_client, message)
        else:
            logging.exception(f"The following error has occurred with sendgrid-{str(e)}")


@celery.task(name='send.email.post.smtp')
def send_email_task_smtp(payload):
    smtp_config = get_smtp_config()
    mailer_config = {'transport': {'use': 'smtp', **smtp_config}}

    mailer = Mailer(mailer_config)
    mailer.start()
    message = Message(author=payload['from'], to=payload['to'])
    message.subject = payload['subject']
    message.plain = strip_tags(payload['html'])
    message.rich = payload['html']
    if payload['bcc'] is not None:
        message.bcc = payload['bcc']
    if payload['reply_to'] is not None:
        message.reply = payload['reply_to']
    if payload['attachments'] is not None:
        for attachment in payload['attachments']:
            message.attach(name=attachment)
    try:
        mailer.send(message)
        logging.info('Message sent via SMTP')
    except urllib.error.HTTPError as e:
        if e.code == 554:
            empty_attachments_send(mailer, message)
    mailer.stop()


@celery.task(base=RequestContextTask, name='resize.event.images', bind=True)
def resize_event_images_task(self, event_id, original_image_url):
    event = Event.query.get(event_id)
    try:
        logging.info(f'Event image resizing tasks started {original_image_url}')
        uploaded_images = create_save_image_sizes(
            original_image_url, 'event-image', event.id
        )
        event.large_image_url = uploaded_images['large_image_url']
        event.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        event.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(event)
        logging.info(f'Resized images saved successfully for event with id: {event_id}')
    except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL):
        logging.exception(
            'Error encountered while generating resized images for event with id: {}'.format(
                event_id
            )
        )


@celery.task(base=RequestContextTask, name='resize.exhibitor.images', bind=True)
def resize_exhibitor_images_task(self, exhibitor_id, photo_url):
    exhibitor = Exhibitor.query.get(exhibitor_id)
    try:
        logging.info(
            'Exhibitor image resizing tasks started for exhibitor with id {}: {}'.format(
                exhibitor_id, photo_url
            )
        )
        uploaded_images = create_save_image_sizes(
            photo_url, 'event-image', exhibitor_id, folder='exhibitors'
        )
        exhibitor.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        save_to_db(exhibitor)
        logging.info(
            f'Resized images saved successfully for exhibitor with id: {exhibitor_id}'
        )
    except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL, OSError):
        logging.exception(
            'Error encountered while generating resized images for exhibitor with id: {}'.format(
                exhibitor_id
            )
        )


@celery.task(base=RequestContextTask, name='resize.group.images', bind=True)
def resize_group_images_task(self, group_id, banner_url):
    group = Group.query.get(group_id)
    try:
        logging.info(
            'Group image resizing tasks started for group with id {}: {}'.format(
                group_id, banner_url
            )
        )
        uploaded_images = create_save_image_sizes(
            banner_url, 'event-image', group.id
        )

        group.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        save_to_db(group)
        logging.info(f'Resized images saved successfully for group with id: {group_id}')
    except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL, OSError):
        logging.exception(
            'Error encountered while generating resized images for group with id: {}'.format(
                group_id
            )
        )


@celery.task(base=RequestContextTask, name='resize.user.images', bind=True)
def resize_user_images_task(self, user_id, original_image_url):
    user = safe_query(User, 'id', user_id, 'user_id')
    try:
        logging.info(f'User image resizing tasks started {original_image_url}')
        uploaded_images = create_save_image_sizes(
            original_image_url, 'speaker-image', user.id
        )
        user.original_image_url = uploaded_images['original_image_url']
        user.avatar_url = uploaded_images['original_image_url']
        user.small_image_url = uploaded_images['thumbnail_image_url']
        user.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        user.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(user)
        logging.info(f'Resized images saved successfully for user with id: {user_id}')
    except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL):
        logging.exception(
            'Error encountered while generating resized images for user with id: {}'.format(
                user_id
            )
        )


@celery.task(base=RequestContextTask, name='sponsor.logo.urls', bind=True)
def sponsor_logos_url_task(self, event_id):
    sponsors = Sponsor.query.filter_by(event_id=event_id, deleted_at=None).all()
    for sponsor in sponsors:
        try:
            logging.info(f'Sponsor logo url generation task started {sponsor.logo_url}')
            new_logo_url = create_save_resized_image(
                image_file=sponsor.logo_url, resize=False
            )
            sponsor.logo_url = new_logo_url
            save_to_db(sponsor)
            logging.info('Sponsor logo url successfully generated')
        except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL):
            logging.exception('Error encountered while logo generation')


@celery.task(base=RequestContextTask, name='resize.speaker.images', bind=True)
def resize_speaker_images_task(self, speaker_id, photo_url):
    speaker = Speaker.query.get(speaker_id)
    try:
        logging.info(
            'Speaker image resizing tasks started for speaker with id {}'.format(
                speaker_id
            )
        )
        uploaded_images = create_save_image_sizes(photo_url, 'speaker-image', speaker_id)
        speaker.small_image_url = uploaded_images['small_image_url']
        speaker.thumbnail_image_url = uploaded_images['thumbnail_image_url']
        speaker.icon_image_url = uploaded_images['icon_image_url']
        save_to_db(speaker)
        logging.info(
            f'Resized images saved successfully for speaker with id: {speaker_id}'
        )
    except (requests.exceptions.HTTPError, requests.exceptions.InvalidURL):
        logging.exception(
            'Error encountered while generating resized images for event with id: {}'.format(
                speaker_id
            )
        )


@celery.task(base=RequestContextTask, name='export.event', bind=True)
def export_event_task(self, email, event_id, settings):
    event = safe_query(Event, 'id', event_id, 'event_id')
    smtp_encryption = get_settings()['smtp_encryption']
    try:
        logging.info('Exporting started')
        path = event_export_task_base(event_id, settings)
        # task_id = self.request.id.__str__()  # str(async result)
        download_url = path

        result = {'download_url': download_url}

        logging.info('Exporting done.. sending email')
        if check_smtp_config(smtp_encryption):
            send_export_mail(
                email=email, event_name=event.name, download_url=download_url
            )
        else:
            logging.warning('Error in sending export success email')
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.warning('Error in exporting.. sending email')
        if check_smtp_config(smtp_encryption):
            send_export_mail(email=email, event_name=event.name, error_text=str(e))
        else:
            logging.warning('Error in sending export error email')
    return result


@celery.task(base=RequestContextTask, name='import.event', bind=True)
def import_event_task(self, email, file, source_type, creator_id):
    """Import Event Task"""
    task_id = self.request.id.__str__()  # str(async result)
    try:
        logging.info('Importing started')
        result = import_event_task_base(self, file, source_type, creator_id)
        update_import_job(task_id, result['id'], 'SUCCESS')
        logging.info('Importing done..Sending email')
        send_import_mail(
            email=email, event_name=result['event_name'], event_url=result['url']
        )
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.warning('Error in importing the event')
        update_import_job(
            task_id, str(e), e.status if hasattr(e, 'status') else 'FAILURE'
        )
        send_import_mail(email=email, error_text=str(e))

    return result


@celery.task(base=RequestContextTask, name='export.ical', bind=True)
def export_ical_task(self, event_id, temp=True):
    event = safe_query(Event, 'id', event_id, 'event_id')

    try:
        file_path = generate_ics_file(event_id, temp)

        filename = os.path.basename(file_path)
        ical_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            ical_url = upload(
                ical_file, UPLOAD_PATHS['exports-temp']['ical'].format(event_id=event_id)
            )
        else:
            ical_url = upload(
                ical_file, UPLOAD_PATHS['exports']['ical'].format(event_id=event_id)
            )
        result = {'download_url': ical_url}
        if not temp:
            event.ical_url = ical_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in ical download')

    return result


@celery.task(base=RequestContextTask, name='export.xcal', bind=True)
def export_xcal_task(self, event_id, temp=True):
    event = safe_query(Event, 'id', event_id, 'event_id')

    try:
        if temp:
            filedir = os.path.join(
                current_app.config.get('BASE_DIR'),
                f'static/uploads/temp/{event_id}/',
            )
        else:
            filedir = os.path.join(
                current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/'
            )

        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "xcal.xcs"
        file_path = os.path.join(filedir, filename)
        with open(file_path, "w") as temp_file:
            temp_file.write(str(XCalExporter.export(event_id), 'utf-8'))
        xcal_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            xcal_url = upload(
                xcal_file, UPLOAD_PATHS['exports-temp']['xcal'].format(event_id=event_id)
            )
        else:
            xcal_url = upload(
                xcal_file, UPLOAD_PATHS['exports']['xcal'].format(event_id=event_id)
            )
        result = {'download_url': xcal_url}
        if not temp:
            event.xcal_url = xcal_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in xcal download')

    return result


@celery.task(base=RequestContextTask, name='export.pentabarf', bind=True)
def export_pentabarf_task(self, event_id, temp=True):
    event = safe_query(Event, 'id', event_id, 'event_id')

    try:
        if temp:
            filedir = os.path.join(
                current_app.config.get('BASE_DIR'),
                f'static/uploads/temp/{event_id}/',
            )
        else:
            filedir = os.path.join(
                current_app.config.get('BASE_DIR'), 'static/uploads/' + event_id + '/'
            )

        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = "pentabarf.xml"
        file_path = os.path.join(filedir, filename)
        with open(file_path, "w") as temp_file:
            temp_file.write(str(PentabarfExporter.export(event_id), 'utf-8'))
        pentabarf_file = UploadedFile(file_path=file_path, filename=filename)
        if temp:
            pentabarf_url = upload(
                pentabarf_file,
                UPLOAD_PATHS['exports-temp']['pentabarf'].format(event_id=event_id),
            )
        else:
            pentabarf_url = upload(
                pentabarf_file,
                UPLOAD_PATHS['exports']['pentabarf'].format(event_id=event_id),
            )
        result = {'download_url': pentabarf_url}
        if not temp:
            event.pentabarf_url = pentabarf_url
            save_to_db(event)

    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in pentabarf download')

    return result


@celery.task(base=RequestContextTask, name='export.order.csv', bind=True)
def export_order_csv_task(self, event_id):
    orders = db.session.query(Order).filter_by(event_id=event_id)

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"order-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_orders_csv

            content = export_orders_csv(orders)
            for row in content:
                writer.writerow(row)
        order_csv_file = UploadedFile(file_path=file_path, filename=filename)
        order_csv_url = upload(
            order_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': order_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.order.pdf', bind=True)
def export_order_pdf_task(self, event_id):
    orders = db.session.query(Order).filter_by(event_id=event_id)
    event = db.session.query(Event).filter_by(id=int(event_id)).first()
    discount_code = db.session.query(DiscountCode).filter_by(event_id=event_id)
    try:
        order_pdf_url = create_save_pdf(
            render_template(
                'pdf/orders.html',
                event=event,
                event_id=event_id,
                orders=orders,
                discount_code=discount_code,
            ),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': order_pdf_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting order as pdf')

    return result


@celery.task(base=RequestContextTask, name='export.attendees.csv', bind=True)
def export_attendees_csv_task(self, event_id):
    attendees = db.session.query(TicketHolder).filter_by(event_id=event_id)
    custom_forms = db.session.query(CustomForms).filter_by(
        event_id=event_id, form=CustomForms.TYPE.ATTENDEE, is_included=True
    )
    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"attendees-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_attendees_csv

            content = export_attendees_csv(attendees, custom_forms)
            for row in content:
                writer.writerow(row)
        attendees_csv_file = UploadedFile(file_path=file_path, filename=filename)
        attendees_csv_url = upload(
            attendees_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': attendees_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting attendees list as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.attendees.pdf', bind=True)
def export_attendees_pdf_task(self, event_id):
    attendees = db.session.query(TicketHolder).filter_by(event_id=event_id)
    custom_forms = db.session.query(CustomForms).filter_by(
        event_id=event_id, form=CustomForms.TYPE.ATTENDEE, is_included=True
    )
    try:
        attendees_pdf_url = create_save_pdf(
            render_template(
                'pdf/attendees_pdf.html', holders=attendees, custom_forms=custom_forms
            ),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': attendees_pdf_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting attendees list as PDF')

    return result


@celery.task(base=RequestContextTask, name='export.sessions.csv', bind=True)
def export_sessions_csv_task(self, event_id, status='all'):
    if status not in [
        'all',
        'pending',
        'accepted',
        'confirmed',
        'rejected',
        'withdrawn',
        'canceled',
    ]:
        status = 'all'

    if status == 'all':
        sessions = Session.query.filter(
            Session.event_id == event_id, Session.deleted_at.is_(None)
        ).all()
    else:
        sessions = Session.query.filter(
            Session.state == status,
            Session.event_id == event_id,
            Session.deleted_at.is_(None),
        ).all()

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"sessions-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_sessions_csv

            content = export_sessions_csv(sessions)
            for row in content:
                writer.writerow(row)
        sessions_csv_file = UploadedFile(file_path=file_path, filename=filename)
        sessions_csv_url = upload(
            sessions_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': sessions_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.exception('Error in exporting sessions as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.adminsales.csv', bind=True)
def export_admin_sales_csv_task(self, status='all'):
    current_time = datetime.now(pytz.utc)
    if status not in [
        'all',
        'live',
        'past',
    ]:
        status = 'all'

    if status == 'all':
        sales = Event.query.all()
    elif status == 'live':
        sales = Event.query.filter(
            Event.starts_at <= current_time,
            Event.ends_at >= current_time,
        ).all()
    elif status == 'past':
        sales = Event.query.filter(
            Event.ends_at <= current_time,
        ).all()

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"sales-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_sales_csv

            content = export_sales_csv(sales)
            for row in content:
                writer.writerow(row)
        sales_csv_file = UploadedFile(file_path=file_path, filename=filename)
        sales_csv_url = upload(
            sales_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id='admin', identifier=''),
        )
        result = {'download_url': sales_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.exception('Error in exporting sales as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.speakers.csv', bind=True)
def export_speakers_csv_task(self, event_id, status='all'):

    if status not in [
        'all',
        'pending',
        'accepted',
        'confirmed',
        'rejected',
        'withdrawn',
        'canceled',
        'without_session',
    ]:
        status = 'all'

    if status == 'without_session':
        speakers = Speaker.query.filter(
            Speaker.sessions.is_(None),
            Speaker.event_id == event_id,
            Speaker.deleted_at.is_(None),
        ).all()
    elif status == 'all':
        speakers = Speaker.query.filter(
            Speaker.event_id == event_id, Speaker.deleted_at.is_(None)
        ).all()
    else:
        speakers = Speaker.query.filter(
            Speaker.sessions.any(state=status),
            Speaker.event_id == event_id,
            Speaker.deleted_at.is_(None),
        ).all()

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"speakers-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_speakers_csv

            content = export_speakers_csv(speakers)
            for row in content:
                writer.writerow(row)
        speakers_csv_file = UploadedFile(file_path=file_path, filename=filename)
        speakers_csv_url = upload(
            speakers_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': speakers_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting speakers list as CSV')

    return result


@celery.task(base=RequestContextTask, name='export.sessions.pdf', bind=True)
def export_sessions_pdf_task(self, event_id):
    sessions = db.session.query(Session).filter_by(event_id=event_id)
    try:
        sessions_pdf_url = create_save_pdf(
            render_template('pdf/sessions_pdf.html', sessions=sessions),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': sessions_pdf_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting sessions as PDF')

    return result


@celery.task(base=RequestContextTask, name='export.speakers.pdf', bind=True)
def export_speakers_pdf_task(self, event_id):
    speakers = db.session.query(Speaker).filter_by(event_id=event_id)
    try:
        speakers_pdf_url = create_save_pdf(
            render_template('pdf/speakers_pdf.html', speakers=speakers),
            UPLOAD_PATHS['exports-temp']['pdf'].format(event_id=event_id, identifier=''),
        )
        result = {'download_url': speakers_pdf_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logger.exception('Error in exporting speakers as PDF')

    return result


@celery.task(base=RequestContextTask, name='delete.translations', bind=True)
def delete_translations(self, zip_file_path):
    try:
        os.remove(zip_file_path)
    except:
        logger.exception('Error while deleting translations zip file')


@celery.task(name='rename.chat.room')
def rename_chat_room(event_id):
    event = Event.query.get(event_id)
    rename_rocketchat_room(event)
    logging.info("Rocket chat room renamed successfully")


@celery.task(base=RequestContextTask, name='export.group.followers.csv', bind=True)
def export_group_followers_csv_task(self, group_id):

    followers = UserFollowGroup.query.filter_by(group_id=group_id).all()

    try:
        filedir = os.path.join(current_app.config.get('BASE_DIR'), 'static/uploads/temp/')
        if not os.path.isdir(filedir):
            os.makedirs(filedir)
        filename = f"group-followers-{uuid.uuid1().hex}.csv"
        file_path = os.path.join(filedir, filename)

        with open(file_path, "w") as temp_file:
            writer = csv.writer(temp_file)
            from app.api.helpers.csv_jobs_util import export_group_followers_csv

            content = export_group_followers_csv(followers)
            for row in content:
                writer.writerow(row)
        group_followers_csv_file = UploadedFile(file_path=file_path, filename=filename)
        group_followers_csv_url = upload(
            group_followers_csv_file,
            UPLOAD_PATHS['exports-temp']['csv'].format(event_id='group', identifier=''),
        )
        result = {'download_url': group_followers_csv_url}
    except Exception as e:
        result = {'__error': True, 'result': str(e)}
        logging.exception('Error in exporting group followers as CSV')

    return result
